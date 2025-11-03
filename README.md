# msensor-plot-server

This application starts a Plot server, where clients can configure and stream data points in real time to the configured axis.

## Setup Environment

`source setup_env.sh`

## Start server

`python src/app.py`

## Generate proto definitions

- `python -m grpc_tools.protoc -Iproto_gen=proto --python_out=src --pyi_out=src --grpc_python_out=src proto/plot.proto`