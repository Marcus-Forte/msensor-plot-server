import grpc
from PyQt5 import QtCore
import pyqtgraph as pg

# Import the generated gRPC files
from proto_gen import plot_pb2, plot_pb2_grpc
from google.protobuf import empty_pb2

# --- 1. The gRPC Servicer ---
# This class handles gRPC requests.
# It MUST inherit from QObject to create signals.
class PlotServicer(plot_pb2_grpc.PlotServiceServicer, QtCore.QObject):
    
    # --- Qt Signals ---
    # These signals are the thread-safe way to send data
    # from the gRPC thread to the main Qt GUI thread.
    
    # Signal to add a new axis. Emits the AddAxisRequest object.
    add_axis_signal = QtCore.pyqtSignal(object)
    
    # Signal to add a new point. Emits the streamPoint object.
    add_point_signal = QtCore.pyqtSignal(object)
    
    # (NEW) Signal to remove an axis. Emits the RemoveAxisRequest object.
    remove_axis_signal = QtCore.pyqtSignal(object)

    def __init__(self):
        # We must initialize both parent classes
        plot_pb2_grpc.PlotServiceServicer.__init__(self)
        QtCore.QObject.__init__(self)
        
        # Simple color rotation for new plots
        self.pens = [pg.mkPen('r'), pg.mkPen('g'), pg.mkPen('b'), 
                     pg.mkPen('c'), pg.mkPen('m'), pg.mkPen('y')]
        self.pen_index = 0

    def get_next_pen(self):
        pen = self.pens[self.pen_index]
        self.pen_index = (self.pen_index + 1) % len(self.pens)
        return pen

    # --- gRPC Method Implementation ---
    
    def AddAxis(self, request, context):
        """
        Called by a gRPC client to add a new plot.
        This runs in a gRPC thread.
        """
        print(f"[gRPC] Received AddAxis request for ID: {request.axis_id}")
        
        # Do not modify GUI here. Emit the signal instead.
        # The MainWindow will be connected to this signal.
        self.add_axis_signal.emit(request)
        
        return empty_pb2.Empty()

    # (NEW) Implemented the RemoveAxis method
    def RemoveAxis(self, request, context):
        """
        Called by a gRPC client to remove a plot.
        This runs in a gRPC thread.
        """
        print(f"[gRPC] Received RemoveAxis request for ID: {request.axis_id}")
        
        # Emit the signal to safely remove the plot from the GUI
        self.remove_axis_signal.emit(request)
        
        return empty_pb2.Empty()

    def streamPlot(self, request_iterator, context):
        """
        Called by a gRPC client to stream data points.
        This runs in a gRPC thread.
        """
        print("[gRPC] Client connected for streaming points...")
        try:
            # request_iterator is a blocking generator.
            # The loop will run as long as the client is streaming.
            for point in request_iterator:
                # Emit the signal for each point received
                self.add_point_signal.emit(point)
                
            print("[gRPC] Client finished streaming.")
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                print("[gRPC] Client cancelled stream.")
            else:
                print(f"[gRPC] Stream error: {e}")
                
        return empty_pb2.Empty()

