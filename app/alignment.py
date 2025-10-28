from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QMessageBox, QSlider, QLabel
from PyQt5.QtCore import QSettings, Qt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.signal import savgol_filter, find_peaks
from scipy.interpolate import interp1d, splrep, BSpline
import os

from app.select_calibration_tab import preset_lib
import numpy as np  # kept as in your original file


class AlignmentTab:
    """Controller for the 'Alignment v2.0' tab functionality."""

    def __init__(self, ui, main_window):
        """Initialize the tab with UI elements and data attributes."""
        self.ui = ui
        self.main_window = main_window
        self.import_measurement_tab = main_window.import_measurement_tab
        # self.fitpoints_tab = main_window.fitpoints_tab

        # ---------------------------------------------------------------------
        # Flags & basic parameters
        # ---------------------------------------------------------------------
        self.new_cal_data_available = False
        self.new_meas_data_available = False
        self.new_cal_data_available = False
        self.new_meas_data_available = False
        # print("Initialized new_cal_data_available=False, new_meas_data_available=False")
        self.G_step_distance = 0.3

        # ---------------------------------------------------------------------
        # Global plotting / labeling settings
        # ---------------------------------------------------------------------
        self.G_canvas_aspect_ratio = np.array([544, 300])
        self.G_canvas_size = tuple(self.G_canvas_aspect_ratio)
        self.G_canvas_dpi = 80
        self.G_dat_datatype = "SSRM"
        self.G_cal_data_denomination = "Unspecified quantity [abbr. Units]"
        self.G_dat_denomination = "Unspecified quantity [abbr. Units]"

        # ---------------------------------------------------------------------
        # Data holders (calibration & measurement)
        # ---------------------------------------------------------------------
        self.X_c = np.array([])      # Calibration X data 
        self.Y_c = np.array([])      # Calibration Y data
        self.X_data = np.array([])   # Measurement X data 
        self.Y_data = np.array([])   # Measurement Y data

        self.cal_is_flipped = False
        self.data_is_flipped = False
        self.borders_cal = [0, 0]
        self.borders_data = [0, 0]

        self.cal_imported = False
        self.data_imported = False

        # Persistent settings
        self.settings = QSettings("MyApp", "Alignment")
        self.last_directory = self.settings.value("last_directory", "", type=str)

        # ---------------------------------------------------------------------
        # Alignment parameters
        # ---------------------------------------------------------------------
        self.G_alignment_resolution_t = 1000  # Number of shift steps
        self.G_alignment_resolution_m = 1000  # Number of stretch steps
        self.G_alignment_filterwidth = 7      # Savgol filter window (must be odd)
        self.G_alignment_filterorder = 1      # Savgol filter polynomial order
        self.G_alignment_increase_searcharea = False
        self.G_stretch_allowed_window = [-5, 5]

        print(
            "Alignment parameters initialized: t_res=%d, m_res=%d, filterwidth=%d, "
            "filterorder=%d, increase_searcharea=%s"
            % (
                self.G_alignment_resolution_t,
                self.G_alignment_resolution_m,
                self.G_alignment_filterwidth,
                self.G_alignment_filterorder,
                self.G_alignment_increase_searcharea,
            )
        )

        # ---------------------------------------------------------------------
        # UI: sliders configuration
        # ---------------------------------------------------------------------
        try:
            # DataFilterStrenght_slider
            self.ui.DataFilterStrenght_slider.setMinimum(0)
            self.ui.DataFilterStrenght_slider.setMaximum(24)
            self.ui.DataFilterStrenght_slider.setSingleStep(1)
            self.ui.DataFilterStrenght_slider.setPageStep(1)
            self.ui.DataFilterStrenght_slider.setTickPosition(QSlider.TicksBothSides)
            self.ui.DataFilterStrenght_slider.setTickInterval(2)
            self.ui.DataFilterStrenght_slider.setValue(3)  # (7-1)/2 = 3

            self.slider_value_label = QLabel("3", self.ui.DataFilterStrenght_slider.parent())
            self.slider_value_label.setAlignment(Qt.AlignCenter)
            self.slider_value_label.setStyleSheet("font-size: 12px; color: black;")
            slider_rect = self.ui.DataFilterStrenght_slider.geometry()
            self.slider_value_label.setGeometry(slider_rect.x(), slider_rect.y() - 20, 50, 20)

            self.ui.DataFilterStrenght_slider.valueChanged.connect(
                self.update_DataFilterStrenght_slider_label
            )
            # print("DataFilterStrenght_slider configured: range=0-24, step=1, ticks=2, default=3")
        except AttributeError as e:
            print(f"Error: {e}. Ensure DataFilterStrenght_slider exists in UI.")
            raise SystemExit(1)

        try:
            # FilterOrder_Slider
            self.ui.FilterOrder_Slider.setMinimum(0)
            self.ui.FilterOrder_Slider.setMaximum(2)
            self.ui.FilterOrder_Slider.setSingleStep(1)
            self.ui.FilterOrder_Slider.setPageStep(1)
            self.ui.FilterOrder_Slider.setTickPosition(QSlider.TicksBothSides)
            self.ui.FilterOrder_Slider.setTickInterval(1)
            self.ui.FilterOrder_Slider.setValue(1)

            self.slider_value_label_2 = QLabel("1", self.ui.FilterOrder_Slider.parent())
            self.slider_value_label_2.setAlignment(Qt.AlignCenter)
            self.slider_value_label_2.setStyleSheet("font-size: 12px; color: black;")
            slider_rect_2 = self.ui.FilterOrder_Slider.geometry()
            self.slider_value_label_2.setGeometry(slider_rect_2.x(), slider_rect_2.y() - 20, 50, 20)

            self.ui.FilterOrder_Slider.valueChanged.connect(
                self.update_FilterOrder_Slider_label_2
            )
            # print("FilterOrder_Slider configured: range=0-2, step=1, ticks=1, default=1")
        except AttributeError as e:
            print(f"Error: {e}. Ensure FilterOrder_Slider exists in UI.")
            raise SystemExit(1)

        try:
            # minStretch_slider
            self.ui.minStretch_slider.setMinimum(-20)
            self.ui.minStretch_slider.setMaximum(5)
            self.ui.minStretch_slider.setSingleStep(1)
            self.ui.minStretch_slider.setPageStep(1)
            self.ui.minStretch_slider.setTickPosition(QSlider.TicksBothSides)
            self.ui.minStretch_slider.setTickInterval(5)
            self.ui.minStretch_slider.setValue(-5)

            self.slider_value_label_3 = QLabel("-5", self.ui.minStretch_slider.parent())
            self.slider_value_label_3.setAlignment(Qt.AlignCenter)
            self.slider_value_label_3.setStyleSheet("font-size: 12px; color: black;")
            slider_rect_3 = self.ui.minStretch_slider.geometry()
            self.slider_value_label_3.setGeometry(slider_rect_3.x(), slider_rect_3.y() - 20, 50, 20)

            self.ui.minStretch_slider.valueChanged.connect(
                self.update_minStretch_slider_3_label
            )
            # print("minStretch_slider configured: range=-20-5, step=1, ticks=5, default=-5")
        except AttributeError as e:
            print(f"Error: {e}. Ensure minStretch_slider exists in UI.")
            raise SystemExit(1)

        try:
            # MaxStretch_slider
            self.ui.MaxStretch_slider.setMinimum(5)
            self.ui.MaxStretch_slider.setMaximum(20)
            self.ui.MaxStretch_slider.setSingleStep(1)
            self.ui.MaxStretch_slider.setPageStep(1)
            self.ui.MaxStretch_slider.setTickPosition(QSlider.TicksBothSides)
            self.ui.MaxStretch_slider.setTickInterval(5)
            self.ui.MaxStretch_slider.setValue(5)

            self.slider_value_label_4 = QLabel("5", self.ui.MaxStretch_slider.parent())
            self.slider_value_label_4.setAlignment(Qt.AlignCenter)
            self.slider_value_label_4.setStyleSheet("font-size: 12px; color: black;")
            slider_rect_4 = self.ui.MaxStretch_slider.geometry()
            self.slider_value_label_4.setGeometry(slider_rect_4.x(), slider_rect_4.y() - 20, 50, 20)

            self.ui.MaxStretch_slider.valueChanged.connect(
                self.update_MaxStretch_slider_4_label
            )
            # print("MaxStretch_slider configured: range=5-20, step=1, ticks=5, default=5")
        except AttributeError as e:
            print(f"Error: {e}. Ensure MaxStretch_slider exists in UI.")
            raise SystemExit(1)

        # ---------------------------------------------------------------------
        # Buttons & inputs wiring
        # ---------------------------------------------------------------------
        try:
            self.ui.Import_Calib_button.clicked.connect(self.import_calibration)
            self.ui.Import_Data_button.clicked.connect(self.import_data)
            self.ui.start_alignment_button.clicked.connect(self.redraw_rough_plot)
            self.ui.start_alignment_button.clicked.connect(self.redraw_fine_plot)
            self.ui.start_alignment_button.clicked.connect(self.redraw_final_plot)

            print("Button signals connected: Import_Calib_button, Import_Data_button, Apply_button")

            self.ui.Import_Calib_button.setStyleSheet("background-color: yellow; color: black;")
            self.ui.Import_Data_button.setStyleSheet("background-color: yellow; color: black;")
            self.ui.start_alignment_button.setStyleSheet("background-color: red; color: black;")
            # print("Button colors initialized: Import_Calib_button=yellow, Import_Data_button=yellow, start_alignment_button=red")
        except AttributeError as e:
            print("Error: %s. Ensure Import_Calib_button, Import_Data_button, and start_alignment_button exist in UI." % e)
            raise SystemExit(1)

        try:
            self.ui.Increase_Search_area_checkbox.stateChanged.connect(self.update_searcharea)
            print("Increase_Search_area_checkbox connected")
        except AttributeError as e:
            print(f"Error: {e}. Ensure Increase_Search_area_checkbox exists in UI.")
            raise SystemExit(1)

        try:
            self.ui.Search_resol_shift_lineedit.textChanged.connect(self.update_resolution_t)
            self.ui.Search_resol_Stretch_lineedit.textChanged.connect(self.update_resolution_m)
            print("Search_resol_shift_lineedit and Search_resol_Stretch_lineedit connected")
        except AttributeError as e:
            print(f"Error: {e}. Ensure Search_resol_shift_lineedit and Search_resol_Stretch_lineedit exist in UI.")
            raise SystemExit(1)

        # ---------------------------------------------------------------------
        # Matplotlib canvases
        # ---------------------------------------------------------------------
        self.figure_preview = Figure(figsize=self.G_canvas_aspect_ratio / self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        self.canvas_preview = FigureCanvas(self.figure_preview)
        try:
            self.ui.importfigure_verticalLayout.addWidget(self.canvas_preview)
            # print("Preview canvas added to CalibTab_verticalLayout_2")
        except AttributeError as e:
            print(f"Error: {e}. Ensure CalibTab_verticalLayout_2 exists.")
            raise SystemExit(1)

        self.figure_rough = Figure(figsize=self.G_canvas_aspect_ratio / self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        self.canvas_rough = FigureCanvas(self.figure_rough)
        try:
            self.ui.RoughFigure_verticalLayout.addWidget(self.canvas_rough)
            # print("Rough canvas added to CalibTab_verticalLayout_4")
        except AttributeError as e:
            print(f"Error: {e}. Ensure CalibTab_verticalLayout_4 exists.")
            raise SystemExit(1)

        self.figure_fine = Figure(figsize=self.G_canvas_aspect_ratio / self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        self.canvas_fine = FigureCanvas(self.figure_fine)
        try:
            self.ui.FineAlign_verticalLayout.addWidget(self.canvas_fine)
            # print("Fine canvas added to CalibTab_verticalLayout_5")
        except AttributeError as e:
            print(f"Error: {e}. Ensure CalibTab_verticalLayout_5 exists.")
            raise SystemExit(1)

        self.figure_final = Figure(figsize=self.G_canvas_aspect_ratio / self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        self.canvas_final = FigureCanvas(self.figure_final)
        try:
            self.ui.CalibTab_verticalLayout_3.addWidget(self.canvas_final)
            # print("Final canvas added to CalibTab_verticalLayout_3")
        except AttributeError as e:
            print(f"Error: {e}. Ensure CalibTab_verticalLayout_3 exists.")
            raise SystemExit(1)

        # ---------------------------------------------------------------------
        # Fine alignment iterations
        # ---------------------------------------------------------------------
        self.G_alignment_fine_iterations = 50  # Default value
        try:
            value = self.ui.fine_alignement_lineedit.text()
            if value:
                self.G_alignment_fine_iterations = int(value)
            print("PyQt - AlignmentTab: G_alignment_fine_iterations initialized to %d" % self.G_alignment_fine_iterations)
        except AttributeError:
            print("Warning: fine_alignement_lineedit not found, using default G_alignment_fine_iterations=%d" % self.G_alignment_fine_iterations)
        except ValueError:
            print("Warning: Invalid value in fine_alignement_lineedit, using default G_alignment_fine_iterations=%d" % self.G_alignment_fine_iterations)

        try:
            self.ui.fine_alignement_lineedit.textChanged.connect(self.update_fine_iterations)
            self.update_fine_iterations(self.ui.fine_alignement_lineedit.text())
        except AttributeError:
            print("Warning: fine_alignement_lineedit not found, signal connection failed, using default G_alignment_fine_iterations=50")

    # =========================================================================
    # UI Handlers & parameter updates
    # =========================================================================

    def update_fine_iterations(self, text):
        """Update G_alignment_fine_iterations when fine_alignement_lineedit text changes."""
        try:
            if text:
                self.G_alignment_fine_iterations = int(text)
                print("PyQt - AlignmentTab: G_alignment_fine_iterations updated to %d" % self.G_alignment_fine_iterations)
            else:
                self.G_alignment_fine_iterations = 50
                print("PyQt - AlignmentTab: G_alignment_fine_iterations reverted to default %d" % self.G_alignment_fine_iterations)
        except ValueError:
            self.G_alignment_fine_iterations = 50
            print("Warning: Invalid value '%s' in fine_alignement_lineedit, reverted to default G_alignment_fine_iterations=%d" % (text, self.G_alignment_fine_iterations))

    def update_searcharea(self, state):
        self.G_alignment_increase_searcharea = bool(state)
        print("G_alignment_increase_searcharea updated to: %s" % self.G_alignment_increase_searcharea)

    def update_resolution_t(self, text):
        try:
            self.G_alignment_resolution_t = int(float(text))
            print("G_alignment_resolution_t updated to: %d" % self.G_alignment_resolution_t)
        except ValueError:
            print("Invalid Search_resol_shift_lineedit input, keeping default")

    def update_resolution_m(self, text):
        try:
            self.G_alignment_resolution_m = int(float(text))
            print("G_alignment_resolution_m updated to: %d" % self.G_alignment_resolution_m)
        except ValueError:
            print("Invalid Search_resol_Stretch_lineedit input, keeping default")

    def update_DataFilterStrenght_slider_label(self, value):
        self.slider_value_label.setText(str(value))
        self.G_alignment_filterwidth = value * 2 + 1
        slider = self.ui.DataFilterStrenght_slider
        slider_width = slider.width()
        handle_width = 10
        min_val = slider.minimum()
        max_val = slider.maximum()
        if max_val > min_val:
            fraction = (value - min_val) / (max_val - min_val)
            x_offset = int(fraction * (slider_width - handle_width)) + slider.x()
            self.slider_value_label.setGeometry(x_offset - 25, slider.y() - 20, 50, 20)
        print("DataFilterStrenght_slider value updated: %d, G_alignment_filterwidth=%d" % (value, self.G_alignment_filterwidth))

    def update_FilterOrder_Slider_label_2(self, value):
        self.slider_value_label_2.setText(str(value))
        self.G_alignment_filterorder = value
        slider = self.ui.FilterOrder_Slider
        slider_width = slider.width()
        handle_width = 10
        min_val = slider.minimum()
        max_val = slider.maximum()
        if max_val > min_val:
            fraction = (value - min_val) / (max_val - min_val)
            x_offset = int(fraction * (slider_width - handle_width)) + slider.x()
            self.slider_value_label_2.setGeometry(x_offset - 25, slider.y() - 20, 50, 20)
        print("FilterOrder_Slider value updated: %d, G_alignment_filterorder=%d" % (value, self.G_alignment_filterorder))

    def update_minStretch_slider_3_label(self, value):
        self.slider_value_label_3.setText(str(value))
        slider = self.ui.minStretch_slider
        slider_width = slider.width()
        handle_width = 10
        min_val = slider.minimum()
        max_val = slider.maximum()
        if max_val > min_val:
            fraction = (value - min_val) / (max_val - min_val)
            x_offset = int(fraction * (slider_width - handle_width)) + slider.x()
            self.slider_value_label_3.setGeometry(x_offset - 25, slider.y() - 20, 50, 20)
        self.ui.MaxStretch_slider.setMinimum(value)
        if self.ui.MaxStretch_slider.value() < value:
            self.ui.MaxStretch_slider.setValue(value)
            self.slider_value_label_4.setText(str(value))
        self.G_stretch_allowed_window[0] = value
        print("minStretch_slider value updated: %d, G_stretch_allowed_window=%s" % (value, self.G_stretch_allowed_window))

    def update_MaxStretch_slider_4_label(self, value):
        self.slider_value_label_4.setText(str(value))
        slider = self.ui.MaxStretch_slider
        slider_width = slider.width()
        handle_width = 10
        min_val = slider.minimum()
        max_val = slider.maximum()
        if max_val > min_val:
            fraction = (value - min_val) / (max_val - min_val)
            x_offset = int(fraction * (slider_width - handle_width)) + slider.x()
            self.slider_value_label_4.setGeometry(x_offset - 25, slider.y() - 20, 50, 20)
        self.ui.minStretch_slider.setMaximum(value)
        if self.ui.minStretch_slider.value() > value:
            self.ui.minStretch_slider.setValue(value)
            self.slider_value_label_3.setText(str(value))
        self.G_stretch_allowed_window[1] = value
        print("MaxStretch_slider value updated: %d, G_stretch_allowed_window=%s" % (value, self.G_stretch_allowed_window))

    # =========================================================================
    # Utility helpers
    # =========================================================================

    def get_closest_pxl_to_value(self, X, value):
        idx = np.argmin(np.abs(X - value))
        return idx, X[idx]

    def apply_parameters_to_data(self, X, Y, borders, is_flipped):
        """Apply borders and flip parameters to data."""
        # print(f"Applying parameters: borders={borders}, is_flipped={is_flipped}")

        X_out, Y_out = X.copy(), Y.copy()

        borders_i = [
            int(self.get_closest_pxl_to_value(X_out, borders[0])[0]),
            int(self.get_closest_pxl_to_value(X_out, borders[1])[0]),
        ]
        borders_i = sorted(borders_i)

        if borders_i[0] >= len(X_out) or borders_i[1] >= len(X_out):
            print("Warning: Border indices out of range")
            return X_out, Y_out

        X_out = X_out[borders_i[0] : borders_i[1] + 1]
        Y_out = Y_out[borders_i[0] : borders_i[1] + 1]

        if is_flipped:
            X_out = X_out[::-1]
            Y_out = Y_out[::-1]
            # print(f"Data flipped: X range {np.min(X_out):.3f} to {np.max(X_out):.3f}, Y range {np.min(Y_out):.3f} to {np.max(Y_out):.3f}")

        # print(f"X_out range: {np.min(X_out):.3f} to {np.max(X_out):.3f}, Y_out shape: {Y_out.shape}")
        return X_out, Y_out

    def apply_lin_offset(self, X_cal, Y_cal, X_dat, Y_dat, m, t):
        """Apply linear offset to align X_cal and X_dat ranges."""
        # print(f"Applying lin offset: m={m:.3f}, t={t:.3f}, ...")
        X_cal = m * X_cal + t

        X_dat_low_to_high = np.sign(X_dat[0] - X_dat[-1]) == -1
        X_cal_low_to_high = np.sign(X_cal[0] - X_cal[-1]) == -1

        if np.min(X_cal) > np.min(X_dat):
            cutoff_pxl = int(self.get_closest_pxl_to_value(X_dat, np.min(X_cal))[0])
            if X_dat_low_to_high:
                X_dat = X_dat[cutoff_pxl:]
                Y_dat = Y_dat[cutoff_pxl:]
            else:
                X_dat = X_dat[:cutoff_pxl]
                Y_dat = Y_dat[:cutoff_pxl]
                X_dat = X_dat[::-1]
                Y_dat = Y_dat[::-1]
        else:
            cutoff_pxl = int(self.get_closest_pxl_to_value(X_cal, np.min(X_dat))[0])
            if X_cal_low_to_high:
                X_cal = X_cal[cutoff_pxl:]
                Y_cal = Y_cal[cutoff_pxl:]
            else:
                X_cal = X_cal[:cutoff_pxl]
                Y_cal = Y_cal[:cutoff_pxl]
                X_cal = X_cal[::-1]
                Y_cal = Y_cal[::-1]

        if np.max(X_cal) < np.max(X_dat):
            cutoff_pxl = int(self.get_closest_pxl_to_value(X_dat, np.max(X_cal))[0]) + 1
            if X_dat_low_to_high:
                X_dat = X_dat[:cutoff_pxl]
                Y_dat = Y_dat[:cutoff_pxl]
            else:
                X_dat = X_dat[cutoff_pxl:]
                Y_dat = Y_dat[cutoff_pxl:]
                X_dat = X_dat[::-1]
                Y_dat = Y_dat[::-1]
        else:
            cutoff_pxl = int(self.get_closest_pxl_to_value(X_cal, np.max(X_dat))[0]) + 1
            if X_cal_low_to_high:
                X_cal = X_cal[:cutoff_pxl]
                Y_cal = Y_cal[:cutoff_pxl]
            else:
                X_cal = X_cal[cutoff_pxl:]
                Y_cal = Y_cal[cutoff_pxl:]
                X_cal = X_cal[::-1]
                Y_cal = Y_cal[::-1]

        return X_cal, Y_cal, X_dat, Y_dat

    # =========================================================================
    # State resets
    # =========================================================================

    def reset_calibration_state(self):
        """Reset calibration import state and update button colors."""
        self.cal_imported = False
        self.new_cal_data_available = True
        self.ui.Import_Calib_button.setStyleSheet("background-color: yellow; color: black")
        self.ui.start_alignment_button.setStyleSheet("background-color: red; color: black;")
        # print("Import_Calib_button set to yellow due to new calibration sample selection")
        self.update_start_alignment_button()

    def reset_data_state(self):
        """Reset measurement import state and update button colors."""
        self.data_imported = False
        self.new_meas_data_available = True
        self.ui.Import_Data_button.setStyleSheet("background-color: yellow; color: black")
        # print("Import_Data_button set to yellow due to new measurement file selection")
        self.update_start_alignment_button()

    # =========================================================================
    # Plot helpers
    # =========================================================================

    def Main_plot_function(self, fig, X, Y, is_flipped, borders, Plot_type="line", **kwargs):
        """Plot data on the given figure."""
        # print(f"Plotting: is_flipped={is_flipped}, borders={borders}, Plot_type={Plot_type}")
        X, Y = self.apply_parameters_to_data(X, Y, borders, is_flipped)
        ax = fig.gca()
        if Plot_type == "scatter":
            ax.scatter(X, Y, **kwargs)
        else:
            ax.plot(X, Y, **kwargs)
        Y_range = np.nanmax(Y) - np.nanmin(Y)
        Y_mid = (np.nanmax(Y) + np.nanmin(Y)) / 2
        ax.set_ylim([Y_mid - (Y_range / 2) * 1.03, Y_mid + (Y_range / 2) * 1.03])
        # print(f"Y limits: {ax.get_ylim()}")
        return fig, X, Y

    def draw_xlabel(self, Quantity="Depth", is_log=False):
        """Set x-axis label."""
        ax = self.figure_fine.gca() if self.figure_fine.axes else self.figure_preview.gca()
        if Quantity == "Depth":
            ax.set_xlabel("Depth [µm]")
            
        else:
            label = 'SSRM measured resistance' if self.G_dat_datatype == "SSRM" else self.G_dat_denomination
            if is_log and self.G_dat_datatype == "SSRM":
                label += ' [$log_{10}(\Omega)$]'
            elif self.G_dat_datatype == "SSRM":
                label += ' [$\Omega$]'
            ax.set_xlabel(label, fontsize=10)
            ax.tick_params(axis='both', which='major', labelsize=10)
            ax.tick_params(axis='both', which='minor', labelsize=10)
            # print(f"X label set to {label}")

    def draw_ylabel(self, Quantity="Calibration", is_log=True, figure=None):
        """Set y-label for the specified figure."""
        figure = figure or self.figure_preview
        ax = figure.gca()

        if Quantity == "Calibration":
            if self.main_window.select_calibration_tab.G_cal_setting == 1:
                carrier_label = "p-type" if self.main_window.select_calibration_tab.G_carrier_type == "B" else "n-type"
                identifier = f"{carrier_label} charge carrier concentration"
                unit = "cm$^{-3}$"
            elif self.main_window.select_calibration_tab.G_cal_setting == 2:
                identifier = "SRP measured resistivity ρ"
                unit = "Ωcm"
            elif self.main_window.select_calibration_tab.G_cal_setting == 3:
                ax.set_ylabel(self.main_window.select_calibration_tab.denomination, fontsize=10)
                print(f"Y label set to {self.main_window.select_calibration_tab.denomination}")
                return
            if is_log:
                label = f"{identifier} [$log_{{10}}$({unit})]"
            else:
                label = f"{identifier} [{unit}]"
        elif Quantity == "Data":
            label = "SSRM measured resistance" if self.main_window.import_measurement_tab.G_dat_datatype == "SSRM" else self.main_window.import_measurement_tab.G_dat_denomination
            if is_log and self.G_dat_datatype == "SSRM":
                label += " [$log_{10}(\Omega)$]"
            elif self.G_dat_datatype == "SSRM":
                label += " [$\Omega$]"

        ax.set_ylabel(label, fontsize=10)
        print(f"Y label set to {label}")

    def draw_grid(self):
        """Draw grid on the plot."""
        ax = self.figure_preview.gca()
        ax.grid(color='b', which='minor', ls='-.', lw=0.25)
        ax.grid(color='b', which='major', ls='-.', lw=0.5)
        # print("Grid drawn")

    def update_start_alignment_button(self):
        """Update start_alignment_button color based on import states."""
        if self.cal_imported and self.data_imported and not self.new_cal_data_available and not self.new_meas_data_available:
            self.ui.start_alignment_button.setStyleSheet("background-color: yellow; color: black")
            print("start_alignment_button set to yellow: cal_imported=True, data_imported=True")
        else:
            self.ui.start_alignment_button.setStyleSheet("background-color: red; color: black")
            #print(
            #    "start_alignment_button set to red: cal_imported=%s, data_imported=%s, new_cal_data_available=%s, new_meas_data_available=%s"
            #    % (self.cal_imported, self.data_imported, self.new_cal_data_available, self.new_meas_data_available)
            #)

    def start_alignment_clicked(self):
        """Handle start_alignment_button click to set it to green and trigger redraws."""
        if self.cal_imported and self.data_imported and not self.new_cal_data_available and not self.new_meas_data_available:
            self.ui.start_alignment_button.setStyleSheet("background-color: green; color: black")
            # print("start_alignment_button set to green after click")
            self.redraw_rough_plot()
            self.redraw_fine_plot()
            self.redraw_final_plot()
        else:
            print("Error: Cannot start alignment, imports not completed")
            QMessageBox.critical(
                self.main_window,
                "Error",
                "First import data with buttons above. Red: This step is missing previous steps. Yellow: This step is ready. Green: This step has been done",
            )

    # =========================================================================
    # Data importers
    # =========================================================================

    def import_calibration(self):
        print("Import_Calib_button clicked")
        select_tab = self.main_window.select_calibration_tab
        if select_tab.X_data.size > 1:
            self.X_c = select_tab.X_data_range.copy() 
            self.Y_c = select_tab.Y_data.copy()
            self.cal_is_flipped = select_tab.data_is_flipped
            self.borders_cal = select_tab.borders_data.copy()  
            self.cal_imported = True
            self.new_cal_data_available = False
            print(
                "Calibration imported: X_c min=%.3f, max=%.3f, Y_c min=%.3f, max=%.3f, borders_cal=%s"
                % (np.min(self.X_c), np.max(self.X_c), np.nanmin(self.Y_c), np.nanmax(self.Y_c), self.borders_cal)
            )
            self.ui.Import_Calib_button.setStyleSheet("background-color: green; color: black")
            self.redraw_alignment_preview()
            self.update_start_alignment_button()
        else:
            print("Error: No calibration data available")
            self.ui.Import_Calib_button.setStyleSheet("background-color: red; color: black")
            QMessageBox.critical(self.main_window, "Error", "No calibration data available.")

    def import_data(self):
        print("Import_Data_button clicked")
        try:
            meas_tab = self.main_window.import_measurement_tab

            self.X_data = meas_tab.X_data_range.copy()
            self.Y_data = meas_tab.Y_data.copy()
            self.borders_data = meas_tab.borders_data.copy()
            self.data_is_flipped = meas_tab.data_is_flipped

            print(f"Updated X_data: {self.X_data}")
            print(f"Updated Y_data: {self.Y_data}")
            print(f"Updated Borders: {self.borders_data}")
            print(f"Data Flipped: {self.data_is_flipped}")

            self.data_imported = True
            self.ui.Import_Data_button.setStyleSheet("background-color: green; color: black")
            self.new_meas_data_available = False

            self.redraw_alignment_preview()
            self.update_start_alignment_button()

        except AttributeError as e:
            print(f"Error: {e}. Ensure import_measurement_tab exists.")
            self.ui.Import_Data_button.setStyleSheet("background-color: red; color: black")
            QMessageBox.critical(self.main_window, "Error", "Measurement tab not found. Aborting import.")

    # =========================================================================
    # Preview & Alignment plots
    # =========================================================================

    def redraw_alignment_preview(self):
        """Redraw the alignment preview plot with calibration and measurement data."""
        print("Redrawing alignment preview")
        self.figure_preview.clear()
        ax = self.figure_preview.add_subplot(111)
        print("Preview canvas size: %dx%d" % (self.canvas_preview.size().width(), self.canvas_preview.size().height()))

        if self.cal_imported and self.X_c.size > 1:
            self.figure_preview, X_c, Y_c = self.Main_plot_function(
                self.figure_preview, self.X_c, self.Y_c, self.cal_is_flipped, self.borders_cal, color="r", label="Calibration"
            )
            print("Calibration plotted: is_flipped=%s, X_c range=%.3f to %.3f" % (self.cal_is_flipped, np.min(X_c), np.max(X_c)))
            self.draw_ylabel(Quantity="Calibration", is_log=not self.main_window.select_calibration_tab.scale_cal_data)
            ax.yaxis.label.set_color("red")
            ax.tick_params(axis="y", colors="red")
            self.draw_grid()
            ax.legend(loc="upper left")

        if self.data_imported and self.X_data.size > 1:
            ax2 = ax.twinx()
            ax2.invert_yaxis()
            self.figure_preview, X_data, Y_data = self.Main_plot_function(
                self.figure_preview, self.X_data, self.Y_data, self.data_is_flipped, self.borders_data, color="blue", label="Measurement"
            )
            print("Measurement plotted: is_flipped=%s, X_data range=%.3f to %.3f" % (self.data_is_flipped, np.min(X_data), np.max(X_data)))
            self.draw_ylabel(Quantity="Data", is_log=False)
            ax2.yaxis.label.set_color("blue")
            ax2.tick_params(axis="y", colors="blue")
            ax2.legend(loc="upper right")

        if self.cal_imported or self.data_imported:
            x_min = min(np.min(X_c) if self.cal_imported and X_c.size > 0 else np.inf,
                        np.min(X_data) if self.data_imported and X_data.size > 0 else np.inf)
            x_max = max(np.max(X_c) if self.cal_imported and X_c.size > 0 else -np.inf,
                        np.max(X_data) if self.data_imported and X_data.size > 0 else -np.inf)
            ax.set_xlim(x_min - 0.5, x_max)
            self.draw_xlabel()
            print("X-axis limits: %s" % (ax.get_xlim(),))

        ax.set_xlabel("Depth [µm]")
        ax.set_title("Unaligned Data")
        self.figure_preview.tight_layout()
        self.canvas_preview.draw_idle()
        print("Preview plot drawn")

    # =========================================================================
    # Alignment primitives
    # =========================================================================

    def differentiate_for_peak_finding(self, test_data, filterwidth):
        """Differentiate data for peak finding, with optional smoothing."""
        if filterwidth != 0:
            test_data = savgol_filter(test_data, 1 + filterwidth * 2, 1)
        test_data = np.diff(test_data, 1)
        non_zero = test_data[np.where(test_data != 0)]
        if non_zero.size == 0:
            print("PyQt - Warning: All derivatives are zero, returning zeros")
            return np.zeros_like(test_data)
        test_data = test_data / np.min(np.abs(non_zero))
        test_data = np.abs(test_data)
        print(
            "PyQt - differentiate_for_peak_finding: test_data shape=%s, min=%.3f, max=%.3f"
            % (test_data.shape, np.min(test_data), np.max(test_data))
        )
        return test_data

    def find_step_pos(self, X, Y, Mode="automatic Mode", fixed_filterwidth=None, variable_set="Alignment"):
        step_dist = self.main_window.select_calibration_tab.G_step_distance
        step_num = self.main_window.select_calibration_tab.G_number_of_steps
        if variable_set == "Get Fitpoints":
            #step_dist = self.main_window.fitpoints_tab.G_fit_min_dist
            step_dist = self.main_window.select_calibration_tab.G_step_distance
            #step_num = self.main_window.fitpoints_tab.G_fit_num - int(self.main_window.fitpoints_tab.fit_includeleft) - int(self.main_window.fitpoints_tab.fit_includeright)
            step_num = self.main_window.select_calibration_tab.G_number_of_steps
            print("Thomas - Get Fitpoints: step_dist=%s, step_num=%s" % (step_dist, step_num))
            if step_num < 1:
                print("PyQt - Error: step_num < 1 in Get Fitpoints")
                return None
        else:  # Alignment
            cal_name = self.ui.calib_sample_combobox.currentText()
            preset_key = "Charge carriers -- default" if self.main_window.select_calibration_tab.G_cal_setting == 1 else "Resistivity -- default"
            #step_dist = preset_lib.get(cal_name, {}).get(preset_key, {}).get("-step_distance-")   ## wtf 
            #step_num = preset_lib.get(cal_name, {}).get(preset_key, {}).get("-num_steps-")

        if step_dist is None or step_num is None:
            print("PyQt - Error: Missing step_dist or step_num for %s in %s" % (cal_name, preset_key))
            return None

        x_interval = np.abs(X[-1] - X[0])
        if x_interval == 0:
            print("PyQt - Error: X range is zero, cannot compute steps")
            return None

        step_distance_pxls = max(1, int(step_dist / x_interval * X.size))
        print(
            "PyQt - Step detection: filterwidth=%s, step_dist=%s, step_num=%s, x_interval=%.3f, step_distance_pxls=%d"
            % (fixed_filterwidth, step_dist, step_num, x_interval, step_distance_pxls)
        )

        test_data = self.differentiate_for_peak_finding(Y, fixed_filterwidth)
        height_threshold = np.percentile(test_data, 10) if np.max(test_data) > 0 else 1
        peaks, properties = find_peaks(test_data, distance=step_distance_pxls, height=height_threshold)
        peak_pos_pxls = peaks.tolist()
        peak_height = properties['peak_heights'].tolist()

        if len(peak_pos_pxls) < (step_num - 1):
            print("PyQt - Warning: Found %d peaks, expected %d, retrying with smoothing" % (len(peak_pos_pxls), (step_num - 1)))
            test_data = self.differentiate_for_peak_finding(Y, filterwidth=1)
            peaks, properties = find_peaks(test_data, distance=step_distance_pxls, height=height_threshold)
            peak_pos_pxls = peaks.tolist()
            peak_height = properties['peak_heights'].tolist()

        if len(peak_pos_pxls) < (step_num - 1):
            print("PyQt - Warning: Still found %d peaks, using fallback" % len(peak_pos_pxls))
            total_width = min(x_interval, step_dist * (step_num - 1))
            start = X[0] + step_dist / 2
            end = X[0] + total_width
            peak_pos = np.linspace(start, end, step_num - 1)
        else:
            while len(peak_pos_pxls) > (step_num - 1):
                smallest_peak = peak_height.index(min(peak_height))
                del peak_height[smallest_peak]
                del peak_pos_pxls[smallest_peak]
            peak_pos = X[peak_pos_pxls]

        print("PyQt - Steps found: %d, positions=%s..." % (len(peak_pos), peak_pos[:min(len(peak_pos), 5)]))
        return peak_pos

    # =========================================================================
    # Rough alignment
    # =========================================================================

    def redraw_rough_plot(self):
        """Redraw the rough alignment heatmap and update result labels."""
        print("Redrawing rough alignment plot")
        if self.new_cal_data_available or self.new_meas_data_available or not self.cal_imported or not self.data_imported:
            print("Error: Imports not completed or new data available")
            QMessageBox.critical(
                self.main_window,
                "Error",
                "First import data with buttons above. Red: This step is missing previous steps. Yellow: This step has not been done. Green: This step has been done",
            )
            return

        self.figure_rough.clear()
        ax = self.figure_rough.add_subplot(111)
        print("PyQt - Rough canvas size: %dx%d" % (self.canvas_rough.size().width(), self.canvas_rough.size().height()))

        if self.cal_imported and self.data_imported and self.X_c.size > 1 and self.X_data.size > 1:
            X_cal, Y_cal = self.apply_parameters_to_data(self.X_c, self.Y_c, self.borders_cal, self.cal_is_flipped)
            X_dat, Y_dat = self.apply_parameters_to_data(self.X_data, self.Y_data, self.borders_data, self.data_is_flipped)
            print("PyQt - X_cal range: %.3f to %.3f, Y_cal min=%.3f, max=%.3f" % (np.min(X_cal), np.max(X_cal), np.nanmin(Y_cal), np.nanmax(Y_cal)))
            print("PyQt - X_dat range: %.3f to %.3f, Y_dat min=%.3f, max=%.3f" % (np.min(X_dat), np.max(X_dat), np.nanmin(Y_dat), np.nanmax(Y_dat)))

            cal_name = self.ui.calib_sample_combobox.currentText()
            preset_key = "Charge carriers -- default" if self.main_window.select_calibration_tab.G_cal_setting == 1 else "Resistivity -- default"
            print("PyQt - Calibration sample: %s" % cal_name)
            self.cal_name = cal_name

            steps_c = self.find_step_pos(X_cal, Y_cal, Mode="automatic Mode", fixed_filterwidth=0, variable_set="Alignment")
            if steps_c is None:
                print("PyQt - Error: No steps found, aborting rough plot")
                return
            print("PyQt - Calibration steps: %d, positions=%s..." % (len(steps_c), steps_c[:min(len(steps_c), 5)]))

            G_stretch_allowed_window = [self.ui.minStretch_slider.value(), self.ui.MaxStretch_slider.value()]
            print("PyQt - G_stretch_allowed_window (from sliders): %s" % G_stretch_allowed_window)
            print("PyQt - G_alignment_increase_searcharea: %s" % self.G_alignment_increase_searcharea)

            if self.G_alignment_increase_searcharea:
                t_min = np.min((np.min(X_dat) - np.max(X_cal)) / (np.array(G_stretch_allowed_window) / 100 + 1))
                t_max = np.max((np.max(X_dat) - np.min(X_cal)) / (np.array(G_stretch_allowed_window) / 100 + 1))
            else:
                t_min = np.min((np.min(X_dat) - np.min(steps_c)) / (np.array(G_stretch_allowed_window) / 100 + 1))
                t_max = np.max((np.max(X_dat) - np.max(steps_c)) / (np.array(G_stretch_allowed_window) / 100 + 1))
                if t_max < t_min:
                    t_max, t_min = min(t_min, t_max), max(t_min, t_max)
            print("PyQt - Shift range: t_min=%.3f, t_max=%.3f" % (t_min, t_max))

            t_arr = np.linspace(t_min, t_max, self.G_alignment_resolution_t)
            m_arr = np.linspace(*G_stretch_allowed_window, self.G_alignment_resolution_m) / 100 + 1
            print("PyQt - t_arr range: %.3f to %.3f, length=%d" % (t_arr[0], t_arr[-1], len(t_arr)))
            print("PyQt - m_arr range: %.3f to %.3f, length=%d" % (m_arr[0], m_arr[-1], len(m_arr)))
            print("PyQt - G_alignment_resolution_t: %d, G_alignment_resolution_m: %d" % (self.G_alignment_resolution_t, self.G_alignment_resolution_m))

            mx_arr = np.einsum('i,j->ij', m_arr, steps_c)
            mxt_arr = np.expand_dims(mx_arr, 1) + t_arr[None, :, None]
            try:
                Y_input = np.abs(savgol_filter(np.diff(Y_dat), self.G_alignment_filterwidth, self.G_alignment_filterorder))
                print("PyQt - Y_input (filtered gradient) shape=%s, min=%.3f, max=%.3f, mean=%.3f" % (Y_input.shape, np.min(Y_input), np.max(Y_input), np.mean(Y_input)))
            except Exception as e:
                print("PyQt - Error in savgol_filter: %s" % e)
                QMessageBox.critical(self.main_window, "Error", "Filtering failed. Adjust filter parameters.")
                return

            multi = (np.max(mxt_arr) - np.min(mxt_arr)) / (np.max(X_dat) - np.min(X_dat))
            X_search = np.linspace(np.min(mxt_arr), np.max(mxt_arr), int(X_dat.size * multi))
            Y_interp = interp1d(X_dat[:-1] + (X_dat[1] - X_dat[0]) / 2, Y_input, kind='linear', bounds_error=False, fill_value=0)
            Y_search = Y_interp(X_search)
            print("PyQt - X_search range: %.3f to %.3f, Y_search shape=%s, min=%.3f, max=%.3f" % (np.min(X_search), np.max(X_search), Y_search.shape, np.min(Y_search), np.max(Y_search)))

            X_idx = np.searchsorted(X_search, mxt_arr, side='left')
            X_idx -= (X_search[X_idx] - mxt_arr) > (mxt_arr - X_search[X_idx - 1])
            X_idx[X_idx < 0] = 0
            quality = np.sum(Y_search[X_idx], axis=2)
            print("PyQt - Quality matrix shape: %s, min=%.7f, max=%.3f, mean=%.3f" % (quality.shape, np.min(quality), np.max(quality), np.mean(quality)))

            optimal_t = np.mean(t_arr[np.where(quality == np.max(quality))[1]])
            optimal_m = np.mean(m_arr[np.where(quality == np.max(quality))[0]])
            print("PyQt - Optimal t: %.3f, m: %.3f" % (optimal_t, optimal_m))
            print("PyQt - Rough plot axes: x=[%.3f, %.3f], y=[%.3f, %.3f]" % (t_min, t_max, G_stretch_allowed_window[0], G_stretch_allowed_window[1]))

            try:
                self.ui.label_20.setText(f"{np.max(quality):.2f}")
                self.quality = quality
                self.ui.get_stretch_in_percentage.setText(f"{(optimal_m - 1) * 100:.1f}")
                self.ui.get_shift_in_nm.setText(f"{optimal_t * 1000:.0f}")
                print("PyQt - Updated labels: quality=%.2f, stretch=%.1f%%, shift=%.0fnm" % (np.max(quality), (optimal_m - 1) * 100, optimal_t * 1000))
            except AttributeError as e:
                print(f"Error: {e}. Ensure label_20, get_stretch_in_percentage, and get_shift_in_nm exist in UI.")

            y_min, y_max = G_stretch_allowed_window
            im = ax.imshow(
                quality[::-1, :],
                extent=[t_min, t_max, y_min, y_max],
                aspect=np.abs((t_max - t_min) / (y_max - y_min)),
                cmap="gnuplot",
            )
            x_ticks = np.linspace(t_min, t_max, 4)
            ax.set_xticks(x_ticks)
            ax.set_xticklabels([f"{x:.1f}" for x in x_ticks], rotation=45)
            print("PyQt - X-axis ticks: %s" % x_ticks)

            cbar = self.figure_rough.colorbar(im)
            quality_max = np.max(quality)
            quality_min = np.min(quality)
            cbar_ticks = np.linspace(quality_min, quality_max, 7)
            cbar.set_ticks(cbar_ticks)
            cbar.ax.set_yticklabels([f"{tick:.2f}" for tick in cbar_ticks])
            print("PyQt - Colorbar ticks: %s" % cbar_ticks)

            self.quality = quality
            self.t_arr = t_arr
            self.m_arr = m_arr

            self.ui.start_alignment_button.setStyleSheet("background-color: green; color: black")
            print("start_alignment_button set to green after rough alignment")

            self.main_window.fitpoints_tab.reset_show_Fit_anchor_button_state()
            self.figure_rough.tight_layout()
            self.canvas_rough.draw_idle()
            print("PyQt - Rough plot drawn")

    def ref(self, X_cal):
        """Map X_cal to corresponding Y_dat values using nearest-neighbor matching."""
        X_dat = self.X_data
        Y_dat = self.Y_data
        R = np.zeros(X_cal.shape)
        for i in range(X_cal.shape[0]):
            R[i] = Y_dat[np.argmin(np.abs(X_cal[i] - X_dat))]
        return R

    def estimate_plateaus(self, X, Y, plot_plateau=True, variable_set="Alignment"):
        """Estimate plateau positions for red bars."""
        step_dist = self.G_step_distance
        print("Step distance:", step_dist)

        step_pos = self.find_step_pos(X, Y, "automatic Mode", fixed_filterwidth=0, variable_set=variable_set)
        if step_pos is None:
            print("Error: Could not find all required steps!")
            return None, None

        x_0 = X[0]
        x_f = X[-1]
        estimate_plateaus_pos = [(x_0 + step_pos[0]) / 2]
        for i in range(len(step_pos) - 1):
            estimate_plateaus_pos.append((step_pos[i] + step_pos[i + 1]) / 2)
        estimate_plateaus_pos.append((step_pos[-1] + x_f) / 2)

        if plot_plateau:
            # The drawing of bars was commented in your original; preserved lines:
            # y_min, y_max = ax.get_ylim()
            # ax.bar(estimate_plateaus_pos, y_max - y_min, bottom=y_min,
            #        alpha=0.25, width=step_dist, color='r', edgecolor='k')
            pass

        print("Plateau positions:", estimate_plateaus_pos)
        return estimate_plateaus_pos, step_pos

    # =========================================================================
    # Fine alignment
    # =========================================================================

    def finealign_profiles_via_spline_matching(self, X_cal, Y_cal, X_dat, Y_dat, m, t, plot=False):
        """Perform fine alignment using spline matching, return quality score or plot."""
        arr_factor = 5
        window_param = 51
        window_order = 1
        inter_s = 0.5
        inter_k = 2

        X_cal, Y_cal, X_dat, Y_dat = self.apply_lin_offset(X_cal, Y_cal, X_dat, Y_dat, m, t)

        X_plateaus_cal, step_pos = self.estimate_plateaus(X_cal, Y_cal, plot_plateau=False, variable_set="Alignment")
        Y_plateaus_cal = [Y_cal[self.get_closest_pxl_to_value(X_cal, i)[0]] for i in X_plateaus_cal]
        X_plateaus_cal = [X_cal[self.get_closest_pxl_to_value(Y_cal, i)[0]] for i in Y_plateaus_cal]
        X_plateaus_dat = [X_dat[self.get_closest_pxl_to_value(X_dat, i)[0]] for i in X_plateaus_cal]
        Y_plateaus_dat = [Y_dat[self.get_closest_pxl_to_value(X_dat, i)[0]] for i in X_plateaus_dat]

        if self.main_window.select_calibration_tab.G_cal_setting == 1:
            plateau_order = sorted(range(len(Y_plateaus_cal)), key=lambda k: Y_plateaus_cal[k])[::-1]
        else:
            plateau_order = sorted(range(len(Y_plateaus_cal)), key=lambda k: Y_plateaus_cal[k])

        Y_plateaus_cal = [Y_plateaus_cal[i] for i in plateau_order]
        Y_plateaus_dat = [Y_plateaus_dat[i] for i in plateau_order]

        my_data = np.c_[self.ref(X_cal), Y_cal]
        my_data = my_data[my_data[:, 0].argsort()]

        x_spaced = np.linspace(my_data[0, 0], my_data[-1, 0], my_data.shape[0] * arr_factor)
        y_spaced = np.zeros(x_spaced.shape)
        for i in range(x_spaced.size):
            closest_idx = np.sort(np.argsort(np.abs(x_spaced[i] - my_data[:, 0]))[:2])
            if np.diff(my_data[:, 0][closest_idx]) == 0:
                y_spaced[i] = my_data[closest_idx[0], 1]
            else:
                y_spaced[i] = np.interp(x_spaced[i], my_data[:, 0][closest_idx], my_data[:, 1][closest_idx])

        y_spaced = savgol_filter(y_spaced, window_param, window_order)

        diff_left = []
        diff_right = []
        for i in range(len(Y_plateaus_dat) - 1):
            slice_point_left = np.argmin(np.abs(Y_plateaus_dat[i] - x_spaced))
            slice_point_right = np.argmin(np.abs(Y_plateaus_dat[i + 1] - x_spaced))
            if slice_point_right == slice_point_left:
                diff_left.append(np.min(Y_cal))
                diff_right.append(np.max(Y_cal))
                break
            elif slice_point_right < slice_point_left:
                slice_point_right, slice_point_left = slice_point_left, slice_point_right

            if slice_point_right - slice_point_left < 3:
                if slice_point_right - slice_point_left < 2:
                    try:
                        slice_point_left -= 1
                        tck = splrep(
                            x_spaced[slice_point_left:slice_point_right],
                            y_spaced[slice_point_left:slice_point_right],
                            s=inter_s,
                            k=1,
                        )
                    except:
                        slice_point_left += 1
                        slice_point_right += 1
                    tck = splrep(
                        x_spaced[slice_point_left:slice_point_right],
                        y_spaced[slice_point_left:slice_point_right],
                        s=inter_s,
                        k=1,
                    )
                else:
                    tck = splrep(
                        x_spaced[slice_point_left:slice_point_right],
                        y_spaced[slice_point_left:slice_point_right],
                        s=inter_s,
                        k=1,
                    )
            else:
                tck = splrep(
                    x_spaced[slice_point_left:slice_point_right],
                    y_spaced[slice_point_left:slice_point_right],
                    s=inter_s,
                    k=inter_k,
                )

            spline = BSpline(*tck)(x_spaced[slice_point_left:slice_point_right])
            diff_left.append(np.diff(spline)[0])
            diff_right.append(np.diff(spline)[-1])

            if plot:
                ax = self.figure_fine.gca()
                ax.plot(x_spaced[slice_point_left:slice_point_right], spline, ls="--", color="r", lw=2)

        if plot:
            ax = self.figure_fine.gca()
            ax.scatter(self.ref(X_cal), Y_cal, color="blue", alpha=0.25, label="Datapoints")
            self.draw_xlabel(Quantity="Data", is_log=False)
            self.draw_ylabel(
                Quantity="Calibration",
                is_log=not self.main_window.select_calibration_tab.scale_cal_data,
                figure=self.figure_fine,
            )
            # self.draw_grid()
            ax.scatter(Y_plateaus_dat, Y_plateaus_cal, color="red", alpha=1, label="Plateau points")
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles, labels, loc="best", fontsize=10)
            self.figure_fine.tight_layout()

        return np.sum(np.abs(np.array(diff_left[1:]) - np.array(diff_right[:-1])))

    def redraw_fine_plot(self):
        """Redraw the fine alignment plot in FineAlign_verticalLayout."""
        print("Redrawing fine alignment plot")
        self.figure_fine.clear()

        if not (
            self.cal_imported
            and self.data_imported
            and self.X_c.size > 1
            and self.X_data.size > 1
            and hasattr(self, 'quality')
        ):
            print("Error: Missing data or rough alignment not performed")
            QMessageBox.critical(self.main_window, "Error", "Perform rough alignment first.")
            return

        X_cal, Y_cal = self.apply_parameters_to_data(self.X_c, self.Y_c, self.borders_cal, self.cal_is_flipped)
        X_dat, Y_dat = self.apply_parameters_to_data(self.X_data, self.Y_data, self.borders_data, self.data_is_flipped)

        quality_ = np.copy(self.quality)
        best_fits = np.zeros((2, self.G_alignment_fine_iterations))
        print("PyQt2222 - AlignmentTab: G_alignment_fine_iterations set to****************************************************** %d" % self.G_alignment_fine_iterations)

        for i in range(self.G_alignment_fine_iterations):
            max_index = np.argwhere(quality_ == np.max(quality_))[0]
            best_fits[:, i] = max_index
            quality_[tuple(max_index)] = 0

        quals = np.zeros(self.G_alignment_fine_iterations)
        for i in range(self.G_alignment_fine_iterations):
            try:
                quals[i] = self.finealign_profiles_via_spline_matching(
                    X_cal, Y_cal, X_dat, Y_dat, self.m_arr[int(best_fits[0, i])], self.t_arr[int(best_fits[1, i])]
                )
            except Exception as e:
                print(f"Error in spline generation: {e}")
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    "Spline generation failed. Try decreasing number of steps or increasing data size.",
                )
                return

        i = np.argmin(quals)
        self.best_m = self.m_arr[int(best_fits[0, i])]
        self.best_t = self.t_arr[int(best_fits[1, i])]
        print("Fine alignment results: quality=%.7f, stretch=%.1f%%, shift=%.0fnm" % (quals[i], (self.best_m - 1) * 100, self.best_t * 1000))

        self.quality = quals[i]
        self.finealign_profiles_via_spline_matching(X_cal, Y_cal, X_dat, Y_dat, self.best_m, self.best_t, plot=True)

        try:
            self.ui.get_stretch_in_percentage.setText(f"{(self.best_m - 1) * 100:.1f}")
            self.ui.get_shift_in_nm.setText(f"{self.best_t * 1000:.0f}")
            self.ui.label_20.setText(f"{quals[i]:.2f}")
            self.quals = quals
        except AttributeError as e:
            print(f"Error: {e}. Ensure get_stretch_in_percentage, get_shift_in_nm, and label_20 exist in UI.")

        ax = self.figure_fine.gca()
        ax.grid(color='b', which='minor', ls='-.', lw=0.25)
        ax.grid(color='b', which='major', ls='-.', lw=0.5)
        print("Grid drawn on fine plot")

        self.canvas_fine.draw_idle()
        print("Fine plot drawn")
        self.redraw_final_plot()

    # =========================================================================
    # Final aligned plot
    # =========================================================================

    def redraw_final_plot(self):
        """Redraw the final alignment plot in CalibTab_verticalLayout_3."""
        print("Redrawing final alignment plot")
        self.figure_final.clear()

        if not (
            self.cal_imported
            and self.data_imported
            and self.X_c.size > 1
            and self.X_data.size > 1
            and hasattr(self, 'best_m')
            and hasattr(self, 'best_t')
        ):
            print("Error: Missing data or fine alignment not performed")
            QMessageBox.critical(self.main_window, "Error", "Perform fine alignment first.")
            return

        X_cal, Y_cal = self.apply_parameters_to_data(self.X_c, self.Y_c, self.borders_cal, self.cal_is_flipped)
        X_dat, Y_dat = self.apply_parameters_to_data(self.X_data, self.Y_data, self.borders_data, self.data_is_flipped)

        # Apply optimal stretch and shift from fine alignment
        X_cal = self.best_m * X_cal + self.best_t

        # Cut profiles to common X-range
        X_dat_low_to_high = np.sign(X_dat[0] - X_dat[-1]) == -1
        X_cal_low_to_high = np.sign(X_cal[0] - X_cal[-1]) == -1

        if np.min(X_cal) > np.min(X_dat):
            cutoff_pxl = int(self.get_closest_pxl_to_value(X_dat, np.min(X_cal))[0])
            if X_dat_low_to_high:
                X_dat = X_dat[cutoff_pxl:]
                Y_dat = Y_dat[cutoff_pxl:]
            else:
                X_dat = X_dat[:cutoff_pxl]
                Y_dat = Y_dat[:cutoff_pxl]
                X_dat = X_dat[::-1]
                Y_dat = Y_dat[::-1]
        else:
            cutoff_pxl = int(self.get_closest_pxl_to_value(X_cal, np.min(X_dat))[0])
            if X_cal_low_to_high:
                X_cal = X_cal[cutoff_pxl:]
                Y_cal = Y_cal[cutoff_pxl:]
            else:
                X_cal = X_cal[:cutoff_pxl]
                Y_cal = Y_cal[:cutoff_pxl]
                X_cal = X_cal[::-1]
                Y_cal = Y_cal[::-1]

        if np.max(X_cal) < np.max(X_dat):
            cutoff_pxl = int(self.get_closest_pxl_to_value(X_dat, np.max(X_cal))[0]) + 1
            if X_dat_low_to_high:
                X_dat = X_dat[:cutoff_pxl]
                Y_dat = Y_dat[:cutoff_pxl]
            else:
                X_dat = X_dat[cutoff_pxl:]
                Y_dat = Y_dat[cutoff_pxl:]
                X_dat = X_dat[::-1]
                Y_dat = Y_dat[::-1]
        else:
            cutoff_pxl = int(self.get_closest_pxl_to_value(X_cal, np.max(X_dat))[0]) + 1
            if X_cal_low_to_high:
                X_cal = X_cal[:cutoff_pxl]
                Y_cal = Y_cal[:cutoff_pxl]
            else:
                X_cal = X_cal[cutoff_pxl:]
                Y_cal = Y_cal[cutoff_pxl:]
                X_cal = X_cal[::-1]
                Y_cal = Y_cal[::-1]

        print(
            "Final plot - X_cal range: %.3f to %.3f, Y_cal min=%.3f, max=%.3f"
            % (np.min(X_cal), np.max(X_cal), np.nanmin(Y_cal), np.nanmax(Y_cal))
        )
        print(
            "Final plot - X_dat range: %.3f to %.3f, Y_dat min=%.3f, max=%.3f"
            % (np.min(X_dat), np.max(X_dat), np.nanmin(Y_dat), np.nanmax(Y_dat))
        )

        ax = self.figure_final.add_subplot(111)
        ax.set_title("Aligned Data")
        ax.plot(X_cal, Y_cal, color='r', label='Calibration')
        ax.set_ylabel("Calibration Data")
        ax.yaxis.label.set_color('red')
        ax.tick_params(axis='y', colors='red')
        ax.set_ylim([np.max(Y_cal) - 1.05 * (np.max(Y_cal) - np.min(Y_cal)), np.max(Y_cal) * 1.05])
        ax.legend(loc='upper left')

        ax2 = ax.twinx()
        ax2.plot(X_dat, Y_dat, color='blue', label='Measurement')
        ax2.set_ylabel("Measurement Data")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.set_ylim([np.max(Y_dat) - 1.05 * (np.max(Y_dat) - np.min(Y_dat)), np.max(Y_dat) * 1.05])
        ax2.invert_yaxis()
        ax2.legend(loc='upper right')

        x_min = min(np.min(X_cal), np.min(X_dat))
        x_max = max(np.max(X_cal), np.max(X_dat))
        ax.set_xlim(x_min - 0.5, x_max)
        print("Final plot - X-axis limits: %s" % (ax.get_xlim(),))

        self.main_window.calibration_tab.reset_buttons_state()

        self.figure_final.tight_layout()
        self.canvas_final.draw_idle()
        print("Final plot drawn")
