from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QSettings
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.signal import savgol_filter
import os

class AlignmentTab:
    """Controller for the 'Alignment v2.0' tab functionality."""
    def __init__(self, ui, main_window):
        """Initialize the tab with UI elements and data attributes."""
        self.ui = ui
        self.main_window = main_window

        # Global settings
        self.G_canvas_aspect_ratio = np.array([544, 300])
        self.G_canvas_size = tuple(self.G_canvas_aspect_ratio)
        self.G_canvas_dpi = 80
        self.G_dat_datatype = "SSRM"  # Default, adjust if needed
        self.G_cal_data_denomination = "Unspecified quantity [abbr. Units]"
        self.G_dat_denomination = "Unspecified quantity [abbr. Units]"

        # Initialize data attributes
        self.X_c = np.array([])  # Calibration X data (mm)
        self.Y_c = np.array([])  # Calibration Y data
        self.X_data = np.array([])  # Measurement X data (mm)
        self.Y_data = np.array([])  # Measurement Y data
        self.cal_is_flipped = False
        self.data_is_flipped = False
        self.borders_cal = [0, 0]
        self.borders_data = [0, 0]
        self.cal_imported = False
        self.data_imported = False
        self.settings = QSettings("MyApp", "Alignment")
        self.last_directory = self.settings.value("last_directory", "", type=str)

        # Initialize matplotlib canvases
        print("Initializing canvases")
        self.figure_preview = Figure(figsize=self.G_canvas_aspect_ratio/self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        self.canvas_preview = FigureCanvas(self.figure_preview)
        try:
            self.ui.CalibTab_verticalLayout_2.addWidget(self.canvas_preview)
            print("Preview canvas added to CalibTab_verticalLayout_2")
        except AttributeError as e:
            print(f"Error: {e}. Ensure CalibTab_verticalLayout_2 exists.")
            raise SystemExit(1)

        self.figure_rough = Figure(figsize=self.G_canvas_aspect_ratio/self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        self.canvas_rough = FigureCanvas(self.figure_rough)
        try:
            self.ui.CalibTab_verticalLayout_3.addWidget(self.canvas_rough)
            print("Rough canvas added to CalibTab_verticalLayout_3")
        except AttributeError as e:
            print(f"Error: {e}. Ensure CalibTab_verticalLayout_3 exists.")
            raise SystemExit(1)

        self.figure_fine = Figure(figsize=self.G_canvas_aspect_ratio/self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        self.canvas_fine = FigureCanvas(self.figure_fine)
        try:
            self.ui.CalibTab_verticalLayout_4.addWidget(self.canvas_fine)
            print("Fine canvas added to CalibTab_verticalLayout_4")
        except AttributeError as e:
            print(f"Error: {e}. Ensure CalibTab_verticalLayout_4 exists.")
            raise SystemExit(1)

        self.figure_final = Figure(figsize=self.G_canvas_aspect_ratio/self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        self.canvas_final = FigureCanvas(self.figure_final)
        try:
            self.ui.CalibTab_verticalLayout_5.addWidget(self.canvas_final)
            print("Final canvas added to CalibTab_verticalLayout_5")
        except AttributeError as e:
            print(f"Error: {e}. Ensure CalibTab_verticalLayout_5 exists.")
            raise SystemExit(1)

        # Connect button signals
        try:
            self.ui.Import_Calib_button.clicked.connect(self.import_calibration)
            self.ui.Import_Data_button.clicked.connect(self.import_data)
            print("Button signals connected")
        except AttributeError as e:
            print(f"Error: {e}. Ensure Import_Calib_button and Import_Data_button exist in UI.")
            raise SystemExit(1)

    def get_closest_pxl_to_value(self, X, value):
        """Find the index of the closest value in X to the given value."""
        idx = np.argmin(np.abs(X - value))
        return idx, X[idx]

    def apply_parameters_to_data(self, X, Y, borders, is_flipped):
        """Apply borders and flip state to data."""
        print(f"Applying parameters: borders={borders}, is_flipped={is_flipped}")
        borders_i = [int(self.get_closest_pxl_to_value(X, borders[0])[0]),
                     int(self.get_closest_pxl_to_value(X, borders[1])[0])]
        Y = Y[borders_i[0]:borders_i[1]+1]
        X = X[borders_i[0]:borders_i[1]+1]
        if is_flipped:
            X = X[::-1]
            Y = Y[::-1]
        print(f"Output X range: {np.min(X):.3f} to {np.max(X):.3f}, Y min={np.nanmin(Y):.3f}, max={np.nanmax(Y):.3f}")
        return X, Y

    def Main_plot_function(self, fig, X, Y, is_flipped, borders, Plot_type="line", **kwargs):
        """Plot data on the given figure."""
        print(f"Plotting: is_flipped={is_flipped}, borders={borders}, Plot_type={Plot_type}")
        X, Y = self.apply_parameters_to_data(X, Y, borders, is_flipped)
        ax = fig.gca()
        if Plot_type == "scatter":
            ax.scatter(X, Y, **kwargs)
        else:
            ax.plot(X, Y, **kwargs)
        Y_range = np.nanmax(Y) - np.nanmin(Y)
        Y_mid = (np.nanmax(Y) + np.nanmin(Y)) / 2
        ax.set_ylim([Y_mid - (Y_range / 2) * 1.03, Y_mid + (Y_range / 2) * 1.03])
        print(f"Y limits: {ax.get_ylim()}")
        return fig, X, Y

    def draw_xlabel(self, Quantity="Depth", is_log=False):
        """Set x-axis label."""
        if Quantity == "Depth":
            ax = self.figure_preview.gca()
            ax.set_xlabel("Depth [mm]")  # Changed to mm to match SelectCalibrationTab
            print("X label set to Depth [mm]")
        else:
            label = 'SSRM measured resistance' if self.G_dat_datatype == "SSRM" else self.G_dat_denomination
            if is_log and self.G_dat_datatype == "SSRM":
                label += ' [$log_{10}(\Omega)$]'
            elif self.G_dat_datatype == "SSRM":
                label += ' [$\Omega$]'
            ax = self.figure_preview.gca()
            ax.set_xlabel(label, fontsize=10)
            ax.tick_params(axis='both', which='major', labelsize=10)
            ax.tick_params(axis='both', which='minor', labelsize=10)
            print(f"X label set to {label}")

    def draw_ylabel(self, Quantity="Calibration", is_log=True):
        """Set y-axis label."""
        ax = self.figure_preview.gca()
        if Quantity == "Calibration":
            if self.main_window.select_calibration_tab.G_cal_setting == 1:
                identifier = f"{self.main_window.select_calibration_tab.G_carrier_type} charge carrier concentration"
                unit = "cm$^{-3}$"
            elif self.main_window.select_calibration_tab.G_cal_setting == 2:
                identifier = "SRP measured resistivity ρ"
                unit = '$\Omega$cm'
            elif self.main_window.select_calibration_tab.G_cal_setting == 3:
                ax.set_ylabel(self.main_window.select_calibration_tab.denomination)
                print(f"Y label set to {self.main_window.select_calibration_tab.denomination}")
                return
            if is_log:
                label = f"{identifier} [$log_{{10}}$({unit})]"
            else:
                label = f"{identifier} [{unit}]"
        elif Quantity == "Data":
            label = 'SSRM measured resistance' if self.G_dat_datatype == "SSRM" else self.G_dat_denomination
            if is_log and self.G_dat_datatype == "SSRM":
                label += ' [$log_{10}(\Omega)$]'
            elif self.G_dat_datatype == "SSRM":
                label += ' [$\Omega$]'
            ax.set_ylabel(label)
            print(f"Y label set to {label}")
            return
        ax.set_ylabel(label, fontsize=10)
        print(f"Y label set to {label}")

    def draw_grid(self):
        """Draw grid on the plot."""
        ax = self.figure_preview.gca()
        ax.grid(color='b', which='minor', ls='-.', lw=0.25)
        ax.grid(color='b', which='major', ls='-.', lw=0.5)
        print("Grid drawn")

    def import_calibration(self):
        """Import calibration data from SelectCalibrationTab and update preview."""
        print("Import_Calib_button clicked")
        select_tab = self.main_window.select_calibration_tab
        if select_tab.X_data.size > 1:
            self.X_c = select_tab.X_data.copy() * 1e-6  # Convert µm to mm
            self.Y_c = select_tab.Y_data.copy()
            self.cal_is_flipped = select_tab.data_is_flipped
            self.borders_cal = select_tab.borders_data.copy()
            self.cal_imported = True
            print(f"Calibration imported: X_c min={np.min(self.X_c):.3f}, max={np.max(self.X_c):.3f}, Y_c min={np.nanmin(self.Y_c):.3f}, max={np.nanmax(self.Y_c):.3f}")
            self.ui.Import_Calib_button.setStyleSheet("background-color: green; color: black")
            self.redraw_alignment_preview()
        else:
            print("Error: No calibration data available")
            self.ui.Import_Calib_button.setStyleSheet("background-color: red; color: black")
            QMessageBox.critical(self.main_window, "Error", "No calibration data available. Select a sample in the Calibration tab.")

    def import_data(self):
        """Import measurement data from a file and update preview."""
        print("Import_Data_button clicked")
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window, "Select Measurement Data File", self.last_directory, "Text Files (*.txt)"
        )
        if file_path:
            print(f"Selected measurement file: {file_path}")
            self.last_directory = os.path.dirname(file_path)
            self.settings.setValue("last_directory", self.last_directory)
            data = self.load_data(file_path)
            if data is not None:
                self.X_data = data[:, 0] * 1e-6  # Convert µm to mm
                self.X_data = self.X_data - np.min(self.X_data)
                self.Y_data = data[:, 1]
                self.borders_data = [np.min(self.X_data), np.max(self.X_data)]
                self.data_is_flipped = False
                self.data_imported = True
                print(f"Measurement data imported: X_data min={np.min(self.X_data):.3f}, max={np.max(self.X_data):.3f}, Y_data min={np.nanmin(self.Y_data):.3f}, max={np.nanmax(self.Y_data):.3f}")
                self.ui.Import_Data_button.setStyleSheet("background-color: green; color: black")
                self.redraw_alignment_preview()
            else:
                print("Failed to import measurement data")
                self.ui.Import_Data_button.setStyleSheet("background-color: red; color: black")
                QMessageBox.critical(self.main_window, "Error", "Failed to import measurement data.")
        else:
            print("No file selected")
            self.ui.Import_Data_button.setStyleSheet("background-color: yellow; color: black")

    def load_data(self, path_data):
        """Load measurement data from a text file."""
        print(f"Attempting to load measurement file: {path_data}")
        if not os.path.exists(path_data):
            print(f"Error: File does not exist: {path_data}")
            return None
        if not os.access(path_data, os.R_OK):
            print(f"Error: File is not readable: {path_data}")
            return None
        try:
            with open(path_data, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:5]
                print("File preview (first 5 lines):")
                for i, line in enumerate(lines):
                    print(f"Line {i+1}: {line.strip()}")
            data = np.loadtxt(path_data, delimiter=None, usecols=(0, 1))
            print(f"Data shape after load: {data.shape}")
            if len(data.shape) != 2 or data.shape[1] != 2:
                print(f"Invalid shape: {data.shape}")
                return None
            if not np.all(np.isfinite(data)):
                print("Error: Data contains non-numeric or invalid values")
                return None
            return data
        except Exception as e:
            print(f"Failed to load data: {str(e)}")
            return None

    def redraw_alignment_preview(self):
        """Redraw the alignment preview plot with calibration and measurement data."""
        print("Redrawing alignment preview")
        self.figure_preview.clear()
        ax = self.figure_preview.add_subplot(111)
        print(f"Preview canvas size: {self.canvas_preview.size().width()}x{self.canvas_preview.size().height()}")

        if self.cal_imported and self.X_c.size > 1:
            self.figure_preview, X_c, Y_c = self.Main_plot_function(
                self.figure_preview, self.X_c, self.Y_c, self.cal_is_flipped, self.borders_cal, color='r', label='Calibration'
            )
            self.draw_ylabel(Quantity="Calibration", is_log=not self.main_window.select_calibration_tab.scale_cal_data)
            ax.yaxis.label.set_color('red')
            ax.tick_params(axis='y', colors='red')
            self.draw_xlabel()
            self.draw_grid()
            ax.legend(loc='upper left')

        if self.data_imported and self.X_data.size > 1:
            ax2 = ax.twinx()
            ax2.invert_yaxis()
            self.figure_preview, X_data, Y_data = self.Main_plot_function(
                self.figure_preview, self.X_data, self.Y_data, self.data_is_flipped, self.borders_data, color='blue', label='Measurement'
            )
            self.draw_ylabel(Quantity="Data", is_log=True)
            ax2.yaxis.label.set_color('blue')
            ax2.tick_params(axis='y', colors='blue')
            ax2.legend(loc='upper right')

        if self.cal_imported or self.data_imported:
            x_min = min(np.min(self.X_c) if self.cal_imported else np.inf, np.min(self.X_data) if self.data_imported else np.inf)
            x_max = max(np.max(self.X_c) if self.cal_imported else -np.inf, np.max(self.X_data) if self.data_imported else -np.inf)
            ax.set_xlim(x_min - 0.5, x_max)
            print(f"X-axis limits: {ax.get_xlim()}")

        self.figure_preview.tight_layout()
        self.canvas_preview.draw()
        print("Preview plot drawn")