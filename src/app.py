import sys
import grpc
import threading
import argparse  # (NEW) Import argparse
from concurrent import futures

from PyQt5 import QtWidgets
import pyqtgraph as pg

# Import the generated gRPC files
from src.proto_gen import plot_pb2_grpc

# Import our new local classes
from .main_window import MainWindow
from .plot_servicer import PlotServicer

# --- PyQtGraph Global Config ---
pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')

# --- Main execution ---
def main():
    # (NEW) Setup argparse
    parser = argparse.ArgumentParser(description="gRPC Remote Plotter Server")
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        default=50051,
        help='The gRPC port to listen on (default: 50051)'
    )
    args = parser.parse_args()
    port = args.port
    
    # 1. Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    
    # 2. Create the main window
    window = MainWindow()
    
    # 3. Create the gRPC servicer (which is also a QObject)
    servicer = PlotServicer()
    
    # 4. Give the servicer to the window so it can connect signals
    window.set_servicer(servicer)
    
    # 5. Create the gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    plot_pb2_grpc.add_PlotServiceServicer_to_server(servicer, server)
    
    # (MODIFIED) Use the port from argparse
    server.add_insecure_port(f'[::]:{port}')
    
    # 6. Start the gRPC server in a separate thread.
    #    'daemon=True' ensures the thread exits when the main app does.
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    # (MODIFIED) Print the port being used
    print(f"--- gRPC Plot Server running in background on port {port} ---")
    
    # 7. Show the Qt window
    window.show()
    
    # 8. Start the Qt event loop (blocking call in the main thread)
    print("--- Starting Qt GUI ---")
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

