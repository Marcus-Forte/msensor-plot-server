import grpc
import sys
import argparse

# gRPC stubs for your PLOT server
from src.proto_gen import plot_pb2_grpc, plot_pb2

# --- Configuration ---

# --- Plot Configuration ---
AXIS_ID_ACCEL = 1
AXIS_ID_GYRO = 2
SAMPLES_TO_SHOW = 300 # Number of points on the plot

SIGNAL_ID_ACC_X = 10
SIGNAL_ID_ACC_Y = 11
SIGNAL_ID_ACC_Z = 12
SIGNAL_ID_GYRO_X = 20
SIGNAL_ID_GYRO_Y = 21
SIGNAL_ID_GYRO_Z = 22

def main():

    argparser = argparse.ArgumentParser(description="Configure IMU Plots on gRPC Plot Server")

    argparser.add_argument(
        '-a', '--address',
        type=str,
        required=True,
        default='localhost:50051',
        help='Address of the gRPC plot server (default: localhost:50051)'
    )

    args = argparser.parse_args()
    print(f"Connecting to plot server at {args.address} to configure IMU plots...")
    
    try:
        with grpc.insecure_channel(args.address) as channel:
            stub = plot_pb2_grpc.PlotServiceStub(channel)
            
            # 1. Wait for plot server to be ready
            print(f"Connected. Sending configuration...")

            # --- Add Axis 1 (Accelerometer) ---
            stub.AddAxis(plot_pb2.AddAxisRequest(
                axis_id=AXIS_ID_ACCEL,
                number_of_samples=SAMPLES_TO_SHOW,
                plot_title="Accelerometer",
                x_axis_title="Time (samples)",
                y_axis_title="Acceleration (m/s^2)"
            ))
            print(f"  > Added Axis {AXIS_ID_ACCEL} (Accelerometer)")
            
            # Add signals to Axis 1
            stub.AddSignal(plot_pb2.AddSignalRequest(
                axis_id=AXIS_ID_ACCEL, signal_id=SIGNAL_ID_ACC_X, 
                signal_name="Accel X", signal_color="r"
            ))
            stub.AddSignal(plot_pb2.AddSignalRequest(
                axis_id=AXIS_ID_ACCEL, signal_id=SIGNAL_ID_ACC_Y, 
                signal_name="Accel Y", signal_color="g"
            ))
            stub.AddSignal(plot_pb2.AddSignalRequest(
                axis_id=AXIS_ID_ACCEL, signal_id=SIGNAL_ID_ACC_Z, 
                signal_name="Accel Z", signal_color="b"
            ))
            print(f"    > Added signals {SIGNAL_ID_ACC_X}, {SIGNAL_ID_ACC_Y}, {SIGNAL_ID_ACC_Z}")

            # --- Add Axis 2 (Gyroscope) ---
            stub.AddAxis(plot_pb2.AddAxisRequest(
                axis_id=AXIS_ID_GYRO,
                number_of_samples=SAMPLES_TO_SHOW,
                plot_title="Gyroscope",
                x_axis_title="Time (samples)",
                y_axis_title="Angular Velocity (deg/s)"
            ))
            print(f"  > Added Axis {AXIS_ID_GYRO} (Gyroscope)")

            # Add signals to Axis 2
            stub.AddSignal(plot_pb2.AddSignalRequest(
                axis_id=AXIS_ID_GYRO, signal_id=SIGNAL_ID_GYRO_X, 
                signal_name="Gyro X", signal_color="c"
            ))
            stub.AddSignal(plot_pb2.AddSignalRequest(
                axis_id=AXIS_ID_GYRO, signal_id=SIGNAL_ID_GYRO_Y, 
                signal_name="Gyro Y", signal_color="m"
            ))
            stub.AddSignal(plot_pb2.AddSignalRequest(
                axis_id=AXIS_ID_GYRO, signal_id=SIGNAL_ID_GYRO_Z, 
                signal_name="Gyro Z", signal_color="y"
            ))
            print(f"    > Added signals {SIGNAL_ID_GYRO_X}, {SIGNAL_ID_GYRO_Y}, {SIGNAL_ID_GYRO_Z}")
            
            print("\nConfiguration complete. Plots are ready.")

    except grpc.FutureTimeoutError:
        print(f"!!! ERROR: Connection timed out. Is the plot server running at {args.address}? !!!")
        sys.exit(1)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
             print(f"!!! ERROR: Plot server is unavailable at {args.address}. Is it running? !!!")
        else:
             print(f"!!! gRPC ERROR: {e.details()} ({e.code()}) !!!")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
