
VERSION := 0.1.0
GRPC_FILES := transfer_pb2.py transfer_pb2.pyi transfer_pb2_grpc.py transfer_pb2_grpc.pyi
GRPC_OUT := $(addprefix flix/lib/proto/,$(GRPC_FILES))
PROTO := flix/lib/proto/transfer.proto

all:build

$(GRPC_OUT): $(PROTO)
	poetry run python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. --mypy_out=. --mypy_grpc_out=. $<

.PHONY: typecheck
typecheck:
	poetry run mypy .

.PHONY: build
build:$(GRPC_OUT) typecheck
	poetry build
