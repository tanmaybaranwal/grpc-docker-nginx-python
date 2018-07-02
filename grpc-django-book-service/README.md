# gRPC + Django Integration with RESTart: gRPC Book Service

gRPC Integration with Django.

This project is tweaked version of https://github.com/tanmaybaranwal/grpc-django-book-service, to implements SSL for server and client.

## Specific to this Django App Workaround:

#### Create a certificate

Make sure you provide a CN:

```sh
$ openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./cert/server.key -out ./cert/server.cert  -subj '/CN=djangoserver'
```

### Export ENV VARS for server:

```sh
$ export SSH_KEY='./cert/server.key'
$ export SSH_CERT='./cert/server.cert'
$ export PORT=50051
```

### Export ENV VARS for client:

```sh
$ export SSL_CERT='./cert/server.cert'
$ export SRV_URL='djangoserver'
$ export SRV_PORT=50051
```

## Django Book Service App:

This project uses internal automation and build tools. The
concerned files and folders in project are:

- grpc_protos
- grpc_utils
- grpc_rest

The Django Application in this project is basic skeleton without
serializers, urls and build files. It contains `views` and it's implementation
which we will be using in `grpc_services`.


## Setup virtualenv

```sh
pip install virtualenv
virtualenv .venv
```

## Install requirements

```bash
$ pip install -r requirements.txt
$ pip install googleapis-common-protos
# if you ran into any issue with kerbrose package install below system dependencies
$ sudo apt-get install krb5-config libkrb5-dev libssl-dev libsasl2-dev libsasl2-modules-gssapi-mit

```

## Running django management commands & usage

```sh
$ source .venv/bin/activate
$ export DJANGO_SETTINGS_MODULE=grpc_book_service_backend.settings.local

# Internal Tools
$ python manage.py build -a grpc_book_service # generate build files
$ python manage.py build -p grpc_book_service # generate protobuf

$ python manage.py makemigrations
$ python manage.py migrate
```

## Running gRPC Server:

```sh
$ python manage.py generate_grpc_stubs grpc_book_service/grpc_protos app.proto

# If importing google.api.annotations:
$ python -m grpc_tools.protoc -I grpc_book_service/grpc_protos --python_out=./grpc_book_service/grpc_protos --grpc_python_out=./grpc_book_service/grpc_protos -I$GOPATH/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis grpc_book_service/grpc_protos/app.proto

# Start gRPC Server
$ python manage.py run_grpc_server grpc_book_service

```

## Connecting to GRPC Using ServiceClient

```python
import os

from grpc_book_service.grpc_protos import app_pb2, app_pb2_grpc
from grpc_book_service.grpc_utils.service_client import ServiceClient

SSL_CERT = os.environ.get('SSL_CERT')
books_service_client = ServiceClient(app_pb2_grpc, 'GRPCBookServiceStub', 'djangoserver', 50051, secure=True, cert=SSL_CERT)
response = books_service_client.GetBookPost(app_pb2.GetBookRequest(isbn=1))

# <response:>
# isbn: 1
# name: "NW-Novel"
# author: "Hiroko Murakami"
# title: "Norwegian Wood"
# codes: 1.0
# codes: 2.5
# codes: 5.5
```

The project also has helper modules from following repos, packages and blogs:

- https://pypi.org/project/grpc-django/
- http://flagzeta.org/blog/using-grpc-with-django/
- https://github.com/grpc-ecosystem/grpc-gateway
- https://github.com/RussellLuo/grpc-pytools
- https://grpc.io/docs/quickstart/python.html
