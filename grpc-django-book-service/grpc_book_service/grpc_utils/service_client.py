import sys
from functools import partial

import grpc


class ServiceClient:

    def __init__(self, service_module, stub_name, host, port, timeout=10,
                 secure=False, **kwargs):

        if secure:
            cert_ = kwargs['cert']
            with open(cert_, 'rb') as f:
                trusted_certs = f.read()

            credentials = grpc.ssl_channel_credentials(
                root_certificates=trusted_certs)
            channel = grpc.secure_channel('{0}:{1}'.format(host, port),
                                          credentials)
        else:
            channel = grpc.insecure_channel('{0}:{1}'.format(host, port))
        try:
            grpc.channel_ready_future(channel).result(timeout=10)
        except grpc.FutureTimeoutError as err:
            print('Error connecting to server')

        self.stub = getattr(service_module, stub_name)(channel)
        self.timeout = timeout

    def __getattr__(self, attr):
        return partial(self._wrapped_call, self.stub, attr)
        
    def _wrapped_call(self, *args, **kwargs):
        try:
            return getattr(args[0], args[1])(
                args[2], timeout=self.timeout, **kwargs
            )
        except grpc.RpcError as e:
            print('Call {0} failed with {1}'.format(
                args[1], e)
            )
            raise
