import sys
from functools import partial

import grpc
import os
from grpc_protos import app_pb2, app_pb2_grpc

class ServiceClient:

    def __init__(self, service_module, stub_name, host, port, timeout=10,
                 secure=False, **kwargs):

        if secure:
            cert_ = kwargs['cert']
            with open(cert_, 'rb') as f:
                trusted_certs = f.read()

            credentials = grpc.ssl_channel_credentials(
                root_certificates=trusted_certs)
            channel = grpc.secure_channel(
                '{0}:{1}'.format(host, port),
                credentials,
                options=(('grpc.ssl_target_name_override', 'nginx',),('grpc.default_authority', 'nginx'),)
            )
        else:
            channel = grpc.insecure_channel('{0}:{1}'.format(host, port))
        try:
            grpc.channel_ready_future(channel).result(timeout=4)
        except grpc.FutureTimeoutError:
            print('Error connecting to server: ', err.message)
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

def connect_client():
    SSL_CERT = os.environ.get('SSL_CERT')
    SRV_URL = os.environ.get('SRV_URL')
    SRV_PORT = os.environ.get('SRV_PORT')

    books_service_client = ServiceClient(app_pb2_grpc, 'GRPCBookServiceStub', SRV_URL, int(SRV_PORT), secure=True, cert=SSL_CERT)
    response = books_service_client.GetBookPost(app_pb2.GetBookRequest(isbn=1))
    print (response)

if __name__ == "__main__":
    connect_client()
