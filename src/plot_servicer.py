import grpc
from PyQt5 import QtCore
import pyqtgraph as pg

# Import the generated gRPC files
from src.proto_gen import  plot_pb2_grpc
from google.protobuf import empty_pb2

# --- 1. The gRPC Servicer ---
# This class handles gRPC requests.
# It MUST inherit from QObject to create signals.
class PlotServicer(plot_pb2_grpc.PlotServiceServicer, QtCore.QObject):
    
    # --- Qt Signals ---
    # These signals are the thread-safe way to send data
    # from the gRPC thread to the main Qt GUI thread.
    
    add_axis_signal = QtCore.pyqtSignal(object)
    remove_axis_signal = QtCore.pyqtSignal(object)
    add_point_signal = QtCore.pyqtSignal(object) # Carries the batch
    
    add_signal_signal = QtCore.pyqtSignal(object)
    remove_signal_signal = QtCore.pyqtSignal(object)
    
    # Signal to clear all plots
    clear_all_signal = QtCore.pyqtSignal()
    

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
        self.add_axis_signal.emit(request)
        return empty_pb2.Empty()

    def RemoveAxis(self, request, context):
        """
        Called by a gRPC client to remove a plot.
        This runs in a gRPC thread.
        """
        print(f"[gRPC] Received RemoveAxis request for ID: {request.axis_id}")
        self.remove_axis_signal.emit(request)
        return empty_pb2.Empty()

    def AddSignal(self, request, context):
        """
        (NEW) Called by a gRPC client to add a line to a plot.
        This runs in a gRPC thread.
        """
        print(f"[gRPC] Received AddSignal request for ID: {request.signal_id} on Axis {request.axis_id}")
        self.add_signal_signal.emit(request)
        return empty_pb2.Empty()

    def RemoveSignal(self, request, context):
        """
        (NEW) Called by a gRPC client to remove a line from a plot.
        This runs in a gRPC thread.
        """
        print(f"[gRPC] Received RemoveSignal request for ID: {request.signal_id}")
        self.remove_signal_signal.emit(request)
        return empty_pb2.Empty()

    # (NEW) gRPC Method for clearAll
    def clearAll(self, request, context):
        """
        (NEW) Called by a gRPC client to remove ALL plots and signals.
        This runs in a gRPC thread.
        """
        print(f"[gRPC] Received clearAll request.")
        self.clear_all_signal.emit()
        return empty_pb2.Empty()


    def streamPlot(self, request_iterator, context):
        """
        Called by a gRPC client to stream data points.
        (MODIFIED to expect batches)
        This runs in a gRPC thread.
        """
        print("[gRPC] Client connected for streaming points...")
        try:
            # request_iterator is a blocking generator.
            # The loop will run as long as the client is streaming.
            for batch in request_iterator:
                # Emit the signal for each batch received
                self.add_point_signal.emit(batch)
                
            print("[gRPC] Client finished streaming.")
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                print("[gRPC] Client cancelled stream.")
            else:
                print(f"[gRPC] Stream error: {e}")
                
        return empty_pb2.Empty()

