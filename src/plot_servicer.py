import grpc
from PyQt5 import QtCore
import pyqtgraph as pg

# Import the generated gRPC files
from src.proto_gen import plot_pb2_grpc
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
    
    # This signal will now emit a BATCH object
    add_point_signal = QtCore.pyqtSignal(object) 
    
    add_signal_signal = QtCore.pyqtSignal(object)
    remove_signal_signal = QtCore.pyqtSignal(object)
    

    def __init__(self):
        # We must initialize both parent classes
        plot_pb2_grpc.PlotServiceServicer.__init__(self)
        QtCore.QObject.__init__(self)
        
        # Simple color rotation for new plots
        self.pens = [pg.mkPen('r'), pg.mkPen('g'), pg.mkPen('b'), 
                     pg.mkPen('c'), pg.mkPen('m'), pg.mkPen('y'),
                     pg.mkPen(color=(255, 165, 0)), # Orange
                     pg.mkPen(color=(238, 130, 238)), # Violet
                    ]
        self.pen_index = 0

    def get_next_pen(self):
        """Used for random color assignment"""
        pen = self.pens[self.pen_index]
        self.pen_index = (self.pen_index + 1) % len(self.pens)
        return pen

    # --- gRPC Method Implementation ---
    
    def AddAxis(self, request, context):
        """
        Called by a gRPC client to add a new plot.
        (Unchanged)
        """
        print(f"[gRPC] Received AddAxis request for ID: {request.axis_id}")
        self.add_axis_signal.emit(request)
        return empty_pb2.Empty()

    def RemoveAxis(self, request, context):
        """
        Called by a gRPC client to remove a plot.
        (Unchanged)
        """
        print(f"[gRPC] Received RemoveAxis request for ID: {request.axis_id}")
        self.remove_axis_signal.emit(request)
        return empty_pb2.Empty()

    def AddSignal(self, request, context):
        """
        Called by a gRPC client to add a new line (signal) to a plot.
        (Unchanged)
        """
        print(f"[gRPC] Received AddSignal request for signal ID: {request.signal_id} on axis ID: {request.axis_id}")
        self.add_signal_signal.emit(request)
        return empty_pb2.Empty()

    def RemoveSignal(self, request, context):
        """
        Called by a gRPC client to remove a line (signal).
        (Unchanged)
        """
        print(f"[gRPC] Received RemoveSignal request for signal ID: {request.signal_id}")
        self.remove_signal_signal.emit(request)
        return empty_pb2.Empty()


    def streamPlot(self, request_iterator, context):
        """
        Called by a gRPC client to stream data points.
        This now iterates over BATCH messages.
        """
        print("[gRPC] Client connected for streaming point batches...")
        try:
            # Iterate over batches, not individual points
            # Assumes the client sends a message containing a 'points' field
            for batch in request_iterator: 
                # Emit the signal with the whole batch
                self.add_point_signal.emit(batch)
                
            print("[gRPC] Client finished streaming.")
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                print("[gRPC] Client cancelled stream.")
            else:
                print(f"[gRPC] Stream error: {e}")
                
        return empty_pb2.Empty()

