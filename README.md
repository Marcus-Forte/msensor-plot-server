# msensor-remote-plotter

This application starts a gRPC plot server, where clients can configure and stream data points in real time.

![gRPC Remote Plotter](./img/sample.png)

Check out the [proto](./proto/plot.proto) definition file to understand the capabilities!

Supports:
* Adding Axes verically.
* Configuring window size.
* Adding and attaching Signals to Axes.
* Streaming Signals.
* Good performance with Qt5.

## Setup Environment

`source setup_env.sh`

## Start server

`python -m src.app -p 50052`

## Configuration

See example for configuring signals of an IMU sensor:

- `python -m config.config_imu_signals -a localhost:50052`

--- 
# Development 

## Generate proto definitions

- `python -m grpc_tools.protoc -Isrc/proto_gen=proto --python_out=. --pyi_out=. --grpc_python_out=. proto/plot.proto`

## TODO

- Error handling