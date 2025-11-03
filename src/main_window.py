import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("gRPC Remote Plotter")
        self.setGeometry(100, 100, 800, 600)

        # Use GraphicsLayoutWidget to dynamically add plots
        self.layoutWidget = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.layoutWidget)

        # Dictionary to store plot info, indexed by axis_id
        # self.plots[axis_id] = {'line': PlotDataItem, 'data': np.array}
        self.plots = {}
        
        # We'll get this from the servicer
        self.servicer = None

    def set_servicer(self, servicer):
        """
        Connects the servicer's signals to this window's slots.
        """
        self.servicer = servicer
        self.servicer.add_axis_signal.connect(self.on_add_axis)
        self.servicer.add_point_signal.connect(self.on_add_point)
        # (NEW) Connect the remove axis signal
        self.servicer.remove_axis_signal.connect(self.on_remove_axis)

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

        # Create the data buffer
        buffer_size = int(request.number_of_samples)
        if buffer_size <= 0:
            buffer_size = 100 # Default
        data_buffer = np.zeros(buffer_size)

        # Create the plot line
        plot_line = plot_item.plot(data_buffer, pen=self.servicer.get_next_pen())
        
        # Store the plot info for later
        self.plots[axis_id] = {
            'plot': plot_item,
            'line': plot_line,
            'data': data_buffer
        }

    # (NEW) Slot to remove the plot
    @QtCore.pyqtSlot(object)
    def on_remove_axis(self, request):
        """
        This function runs in the MAIN GUI THREAD.
        It safely removes a plot from the layout.
        """
        axis_id = request.axis_id
        
        # Atomically remove the plot info from our dictionary
        plot_info = self.plots.pop(axis_id, None)
        
        if not plot_info:
            print(f"[GUI] Warning: Request to remove non-existent axis {axis_id}")
            return
            
        print(f"[GUI] Removing axis: {axis_id}")
        
        # Get the plot item
        plot_item = plot_info['plot']
        
        # Clear it (removes lines)
        plot_item.clear()
        
        # Remove it from the layout widget
        self.layoutWidget.removeItem(plot_item)
        
        # Optional: Ask Qt to delete the C++ object later
        plot_item.deleteLater()

    # --- Qt Slot ---
    @QtCore.pyqtSlot(object)
    def on_add_point(self, point):
        """
        This function runs in the MAIN GUI THREAD.
        It's safe to update the plot.
        """
        axis_id = point.axis_id
        
        # Find the plot info for this axis
        plot_info = self.plots.get(axis_id)
        
        if not plot_info:
            # (MODIFIED) Un-commented this print statement as requested
            # This check is important!
            print(f"[GUI] Warning: Received point for unknown axis {axis_id}")
            return

        # Get the data buffer
        data = plot_info['data']
        
        # Shift data to the left
        data[:-1] = data[1:] 
        
        # Add new point at the end
        data[-1] = point.value
        
        # Update the plot line
        plot_info['line'].setData(data)

