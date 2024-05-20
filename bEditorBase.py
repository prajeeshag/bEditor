import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QAction,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class BathymetryEditorBase(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bathymetry Data Editor")
        self.setGeometry(100, 100, 1000, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.create_menus()

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        # Zooming
        self.canvas.mpl_connect("scroll_event", self.on_mouse_wheel)

        # Panning
        self.canvas.mpl_connect("button_press_event", self.on_button_press_pan)
        self.canvas.mpl_connect("button_release_event", self.on_button_release_pan)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move_pan)
        self.pan_start = None

        self.bathymetry_data = None
        self.patches = []

    def create_menus(self):
        menubar = self.menuBar()

        self.create_menu(
            menubar,
            "File",
            [("Load Data", self.load_data), ("Save Data", self.save_data)],
        )
        self.create_menu(
            menubar,
            "Land",
            [("Find", self.find_islands), ("Delete", self.delete_islands)],
        )
        self.create_menu(
            menubar, "Water", [("Find", self.find_lakes), ("Delete", self.delete_lakes)]
        )

    def create_menu(self, menubar, menu_name, actions):
        menu = menubar.addMenu(menu_name)
        for action_name, action_method in actions:
            action = QAction(action_name, self)
            action.triggered.connect(action_method)
            menu.addAction(action)

    def load_data_from_args(self, nx, ny, bathy_path):
        try:
            self.bathymetry_data = np.fromfile(bathy_path, ">f4").reshape(ny, nx)
            self.update_canvas()
            self.base_xlim = self.ax.get_xlim()
            self.base_ylim = self.ax.get_ylim()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")

    def load_data(self):
        nx, ok = QInputDialog.getInt(self, "Enter NX", "NX (number of columns):")
        if ok:
            ny, ok = QInputDialog.getInt(self, "Enter NY", "NY (number of rows):")
            if ok:
                file_path, _ = QFileDialog.getOpenFileName(
                    self, "Open File", "", "Binary Files (*.bin)"
                )
                if file_path:
                    self.load_data_from_args(int(nx), int(ny), file_path)

    def save_data(self):
        if self.bathymetry_data is not None:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save File", "", "Numpy Files (*.npy)"
            )
            if file_path:
                np.save(file_path, self.bathymetry_data)
        else:
            QMessageBox.critical(self, "Error", "No data to save")

    def update_canvas(self):
        if self.bathymetry_data is not None:
            self.ax.clear()
            self.ax.imshow(self.bathymetry_data, cmap="terrain", origin="lower")
            self.canvas.draw()

    def on_click(self, event):
        if self.edit_mode and self.bathymetry_data is not None:
            # x, y = int(event.xdata), int(event.ydata)
            # Implement pixel editing functionality
            pass

    def on_mouse_wheel(self, event):
        base_scale = 1.1
        if event.button == "up":
            scale_factor = 1 / base_scale
        elif event.button == "down":
            scale_factor = base_scale
        else:
            scale_factor = 1

        curr_xlim = self.ax.get_xlim()
        curr_ylim = self.ax.get_ylim()

        new_width = (curr_xlim[1] - curr_xlim[0]) * scale_factor
        new_height = (curr_ylim[1] - curr_ylim[0]) * scale_factor

        if new_width > (self.base_xlim[1] - self.base_xlim[0]) or new_height > (
            self.base_ylim[1] - self.base_ylim[0]
        ):
            self.ax.set_xlim(self.base_xlim)
            self.ax.set_ylim(self.base_ylim)
        else:
            relx = (curr_xlim[1] - event.xdata) / (curr_xlim[1] - curr_xlim[0])
            rely = (curr_ylim[1] - event.ydata) / (curr_ylim[1] - curr_ylim[0])

            self.ax.set_xlim(
                [event.xdata - new_width * (1 - relx), event.xdata + new_width * relx]
            )
            self.ax.set_ylim(
                [event.ydata - new_height * (1 - rely), event.ydata + new_height * rely]
            )

        self.canvas.draw()

    def on_button_press_pan(self, event):
        if event.button == 1 and event.inaxes:
            self.pan_start = (event.xdata, event.ydata)
            self.pan_xlim = self.ax.get_xlim()
            self.pan_ylim = self.ax.get_ylim()

    def on_mouse_move_pan(self, event):
        if self.pan_start is None or not event.inaxes:
            return
        dx = self.pan_start[0] - event.xdata
        dy = self.pan_start[1] - event.ydata

        self.pan_xlim = (self.pan_xlim[0] + dx, self.pan_xlim[1] + dx)
        self.pan_ylim = (self.pan_ylim[0] + dy, self.pan_ylim[1] + dy)

        self.ax.set_xlim(self.pan_xlim)
        self.ax.set_ylim(self.pan_ylim)
        self.canvas.draw()

    def on_button_release_pan(self, event):
        self.pan_start = None

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode

    def find_islands(self):
        pass

    def delete_islands(self):
        pass

    def find_lakes(self):
        pass

    def delete_lakes(self):
        pass
