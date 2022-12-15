
GRPC_FILES := transfer_pb2.py transfer_pb2.pyi transfer_pb2_grpc.py transfer_pb2_grpc.pyi
GRPC_OUT := $(addprefix flix/lib/proto/,$(GRPC_FILES))
PROTO := flix/lib/proto/transfer.proto

all:build

.download: poetry.lock
	poetry install
	touch $@

$(GRPC_OUT): $(PROTO) .download
	poetry run python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. --mypy_out=. --mypy_grpc_out=. $<

.PHONY: typecheck
typecheck: .download
	poetry run mypy .

.PHONY: build
build:$(GRPC_OUT) typecheck
	poetry build

.PHONY: publish
publish: build
	# requires POETRY_PYPI_TOKEN_PYPI to be set with an api key
	poetry publish

.PHONY: publish_test
publish_test: build
	# requires POETRY_PYPI_TOKEN_TESTPYPI to be set with an api key
	poetry publish -r testpypi
