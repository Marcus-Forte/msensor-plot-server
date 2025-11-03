# msensor-plot-server

This application starts a Plot server, where clients can configure and stream data points in real time to the configured axis.

## Setup Environment

`source setup_env.sh`

## Start server

`python -m src.app -p 50052`

## Generate proto definitions

- `python -m grpc_tools.protoc -Isrc/proto_gen=proto --python_out=. --pyi_out=. --grpc_python_out=. proto/plot.proto`

## Config

Configure plots as IMU:

- `python -m config.config_imu -a localhost:50052`