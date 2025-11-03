import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

# --- 2. The PyQtGraph Main Window ---
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("gRPC Remote Plotter")
        self.setGeometry(100, 100, 800, 600)

        # Use GraphicsLayoutWidget to dynamically add plots
        self.layoutWidget = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.layoutWidget)

        self.plots = {}
        
        #Fast lookup map to find which axis a signal belongs to
        self.signal_to_axis_map = {}
        
        # We'll get this from the servicer
        self.servicer = None

    def set_servicer(self, servicer):
        """
        Connects the servicer's signals to this window's slots.
        """
        self.servicer = servicer
        # Connect all services
        self.servicer.add_axis_signal.connect(self.on_add_axis)
        self.servicer.remove_axis_signal.connect(self.on_remove_axis)
        
        # Connect to the new batch processing slot
        self.servicer.add_point_signal.connect(self.on_add_point_batch) 
        
        self.servicer.add_signal_signal.connect(self.on_add_signal)
        self.servicer.remove_signal_signal.connect(self.on_remove_signal)


    # --- Qt Slot ---
    @QtCore.pyqtSlot(object)
    def on_add_axis(self, request):
        """
        This function runs in the MAIN GUI THREAD.
        It's safe to modify the GUI here.
        """
        axis_id = request.axis_id
        if axis_id in self.plots:
            print(f"[GUI] Axis {axis_id} already exists. Ignoring.")
            return

        print(f"[GUI] Adding axis: {axis_id} ('{request.plot_title}')")
        
        # Add a new plot to the layout
        plot_item = self.layoutWidget.addPlot(row=len(self.plots), col=0)
        
        # Configure the plot
        plot_item.setTitle(request.plot_title, color='k', size="12pt")
        plot_item.setLabel('left', request.y_axis_title)
        plot_item.setLabel('bottom', request.x_axis_title)
        plot_item.showGrid(x=True, y=True, alpha=0.3)
        # Added labelStyle to make the legend font larger
        plot_item.addLegend(brush=pg.mkBrush(50, 50, 50, 150), labelStyle={'color': 'k', 'font-size': '10pt'})

        # Store the plot info for later
        self.plots[axis_id] = {
            'plot': plot_item,
            'number_of_samples': int(request.number_of_samples) if request.number_of_samples > 0 else 100,
            'signals': {} # (NEW) This will hold the lines
        }

    # --- Qt Slot ---
    @QtCore.pyqtSlot(object)
    def on_remove_axis(self, request):
        """
        This function runs in the MAIN GUI THREAD.
        It removes an entire plot and all its associated signals.
        (Unchanged)
        """
        axis_id = request.axis_id
        plot_info = self.plots.pop(axis_id, None) # Safely remove
        
        if plot_info:
            print(f"[GUI] Removing axis: {axis_id}")
            
            # Must also remove all signals from the lookup map
            for signal_id in plot_info['signals'].keys():
                self.signal_to_axis_map.pop(signal_id, None)
                
            # Clear all lines from the plot
            plot_info['plot'].clear()
            # Remove the plot item from the layout
            self.layoutWidget.removeItem(plot_info['plot'])
        else:
            print(f"[GUI] Warning: Tried to remove non-existent axis {axis_id}")

    # --- Qt Slot ---
    @QtCore.pyqtSlot(object)
    def on_add_signal(self, request):
        """
        This function runs in the MAIN GUI THREAD.
        It adds a new line (signal) to an existing plot.
        (MODIFIED to read signal_name)
        """
        axis_id = request.axis_id
        signal_id = request.signal_id
        
        plot_info = self.plots.get(axis_id)
        if not plot_info:
            print(f"[GUI] Error: Cannot add signal {signal_id} to non-existent axis {axis_id}")
            return
            
        if signal_id in self.signal_to_axis_map:
            print(f"[GUI] Error: Signal ID {signal_id} already exists. Ignoring.")
            return

        if signal_id in plot_info['signals']:
             print(f"[GUI] Warning: Signal {signal_id} already in plot, but not in map. (State error)")
             # Continue anyway, overwrite
        
        # Updated print statement
        print(f"[GUI] Adding signal {signal_id} ({request.signal_name}) to axis {axis_id}")

        # Get the pen, check for optional field 'signal_color'
        if request.HasField("signal_color") and request.signal_color:
            try:
                pen = pg.mkPen(request.signal_color)
            except Exception as e:
                print(f"[GUI] Warning: Invalid color '{request.signal_color}'. Using random. Error: {e}")
                pen = self.servicer.get_next_pen()
        else:
            pen = self.servicer.get_next_pen()

        # Create data buffer
        buffer_size = plot_info['number_of_samples']
        data_buffer = np.zeros(buffer_size)
        
        # Use the provided signal_name for the legend
        signal_name = request.signal_name if request.signal_name else f"Signal {signal_id}"

        # Add the line to the plot
        plot_line = plot_info['plot'].plot(data_buffer, pen=pen, name=signal_name)

        # Store the signal info
        plot_info['signals'][signal_id] = {
            'line': plot_line,
            'data': data_buffer
        }
        
        # Add to the fast lookup map
        self.signal_to_axis_map[signal_id] = axis_id
        

    # --- Qt Slot ---
    @QtCore.pyqtSlot(object)
    def on_remove_signal(self, request):
        """
This function runs in the MAIN GUI THREAD.
It removes a single line (signal) from a plot.
(Unchanged)
"""
        signal_id = request.signal_id
        
        axis_id = self.signal_to_axis_map.pop(signal_id, None)
        if axis_id is None:
            print(f"[GUI] Warning: Tried to remove non-existent signal {signal_id}")
            return

        plot_info = self.plots.get(axis_id)
        if not plot_info:
            print(f"[GUI] Error: Signal {signal_id} mapped to non-existent axis {axis_id}")
            return

        signal_info = plot_info['signals'].pop(signal_id, None)
        if signal_info:
            print(f"[GUI] Removing signal {signal_id} from axis {axis_id}")
            plot_info['plot'].removeItem(signal_info['line'])
        else:
            print(f"[GUI] Warning: Signal {signal_id} was in map but not in plot signals dict.")


    # --- Qt Slot ---
    @QtCore.pyqtSlot(object)
    def on_add_point_batch(self, batch): # Renamed from on_add_point
        """
This function runs in the MAIN GUI THREAD.
It processes a BATCH of points.
Signals that are not in the batch will be scrolled with a '0'.
"""
        
        # 1. Create a dictionary of new values from the batch
        #    (Assumes batch message has a 'points' field)
        new_values = {}
        for point in batch.points:
            new_values[point.signal_id] = point.value

        # 2. Get sets of signals
        updated_signals = set(new_values.keys())
        all_known_signals = set(self.signal_to_axis_map.keys())
        
        # 3. Find signals that were *not* updated
        #    (No need for this set, we just check `if signal_id in updated_signals`)
        
        # 4. Check for points sent to unknown signals
        unknown_signals = updated_signals - all_known_signals
        for signal_id in unknown_signals:
            print(f"[GUI] Warning: Received point for unknown signal ID {signal_id}")

        # 5. Process ALL known signals to keep them in sync and scrolling
        for signal_id in all_known_signals:
            axis_id = self.signal_to_axis_map.get(signal_id)
            
            # This should not happen if map is correct, but good to check
            if axis_id is None: 
                continue 
            
            try:
                plot_info = self.plots[axis_id]
                signal_info = plot_info['signals'][signal_id]
            except KeyError:
                print(f"[GUI] Error: State inconsistency. Map has signal {signal_id} but plot {axis_id} does not.")
                continue

            # Get the data buffer
            data = signal_info['data']
            
            # Shift data to the left
            data[:-1] = data[1:] 
            
            # Get the new value
            if signal_id in updated_signals:
                # Use the new value from the batch
                data[-1] = new_values[signal_id]
            else:
                # Use 0.0 for missing signals to keep them scrolling
                data[-1] = 0.0
            
            # Update the plot line
            signal_info['line'].setData(data)


