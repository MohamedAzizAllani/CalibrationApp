from PyQt5.QtWidgets import QMessageBox, QVBoxLayout
from PyQt5.QtCore import Qt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from app.alignment import AlignmentTab

class FitpointsTab:
    """Controller for the 'Fitpoints' tab functionality."""
    def __init__(self, ui, main_window):
        """Initialize the tab with UI elements and data attributes."""
        self.ui = ui
        self.main_window = main_window
        self.alignment_tab = main_window.alignment_tab

        # Global settings
        self.G_canvas_aspect_ratio = np.array([544, 300])
        self.G_canvas_dpi = 80
        self.G_fit_Mode = 'Find fitpoints automatically'
        self.fit_settings_selection = ['Find fitpoints automatically', 'Manually select fitpoints']
        self.G_fit_num = 5
        self.G_fit_min_dist = 1
        self.G_fitpoints = [0, 0, 0, 0]  # Initialize to G_fit_num - 1
        self.G_manual_fitpoints = []
        self.fit_includeleft = False
        self.fit_includeright = False

        # Initialize canvases
        self.figure_fit_overlay = Figure(figsize=self.G_canvas_aspect_ratio/self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        self.canvas_fit_overlay = FigureCanvas(self.figure_fit_overlay)
        try:
            self.ui.fit_overlay_verticalLayout.addWidget(self.canvas_fit_overlay)
            print("Fit overlay canvas added to fit_overlay_verticalLayout")
        except AttributeError as e:
            print(f"Error: {e}. Ensure fit_overlay_verticalLayout exists.")
            raise SystemExit(1)

        self.figure_fit_overlay2 = Figure(figsize=self.G_canvas_aspect_ratio/self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        self.canvas_fit_overlay2 = FigureCanvas(self.figure_fit_overlay2)
        try:
            self.ui.fit_overlay2_verticalLayout.addWidget(self.canvas_fit_overlay2)
            print("Fit overlay2 canvas added to fit_overlay2_verticalLayout")
        except AttributeError as e:
            print(f"Error: {e}. Ensure fit_overlay2_verticalLayout exists.")
            raise SystemExit(1)

        self.figure_fit_cal_curve = Figure(figsize=self.G_canvas_aspect_ratio/self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        self.canvas_fit_cal_curve = FigureCanvas(self.figure_fit_cal_curve)
        try:
            self.ui.fit_cal_curve_verticalLayout.addWidget(self.canvas_fit_cal_curve)
            print("Fit cal curve canvas added to fit_cal_curve_verticalLayout")
        except AttributeError as e:
            print(f"Error: {e}. Ensure fit_cal_curve_verticalLayout exists.")
            raise SystemExit(1)

        # Connect buttons
        try:
            self.ui.Find_fitpoints_Automatically_pushButton.clicked.connect(self.set_auto_mode)
            self.ui.Manually_select_fitpoints_pushButton.clicked.connect(self.set_manual_mode)
            self.ui.Add_pushButton.clicked.connect(self.add_manual_fitpoint)
            self.ui.Undo_pushButton.clicked.connect(self.undo_manual_fitpoint)
            self.ui.Delete_all_pushButton.clicked.connect(self.delete_all_manual_fitpoints)
            self.ui.Fit_go_pushButton.clicked.connect(self.show_fit_anchor_points)
            self.ui.Fit_go_pushButton.clicked.connect(self.fit_go)
            print("Button signals connected")
        except AttributeError as e:
            print(f"Error: {e}. Ensure all buttons exist in UI.")
            raise SystemExit(1)

        # Connect spinbox, line edit, and checkboxes
        try:
            self.ui.Nbr_of_points_spinBox.valueChanged.connect(self.update_fit_num)
            self.ui.Min_distance_between_steps_lineEdit.textChanged.connect(self.update_fit_min_dist)
            self.ui.include_left_edge_as_anchor_checkBox.stateChanged.connect(self.update_include_left)
            self.ui.include_right_edge_as_anchor_checkBox.stateChanged.connect(self.update_include_right)
            self.ui.Num_fitpoints_between_point_1and2_slider.valueChanged.connect(lambda: self.update_fitpoints(1))
            self.ui.Num_fitpoints_between_point_2and3_slider.valueChanged.connect(lambda: self.update_fitpoints(2))
            self.ui.Num_fitpoints_between_point_3and4_slider.valueChanged.connect(lambda: self.update_fitpoints(3))
            self.ui.Num_fitpoints_between_point_4and5_slider.valueChanged.connect(lambda: self.update_fitpoints(4))
            print("SpinBox, LineEdit, CheckBox, and Slider signals connected")
        except AttributeError as e:
            print(f"Error: {e}. Ensure spinbox, lineedit, checkboxes, and sliders exist in UI.")
            raise SystemExit(1)

        # Initialize UI visibility
        self.set_auto_mode()

    def set_auto_mode(self):
        """Set fit mode to automatic and update UI visibility."""
        self.G_fit_Mode = self.fit_settings_selection[0]
        print(f"G_fit_Mode set to: {self.G_fit_Mode}")
        self.ui.Find_fitpoints_Automatically_pushButton.setStyleSheet("background-color: green; color: black")
        self.ui.Manually_select_fitpoints_pushButton.setStyleSheet("background-color: none; color: black")
        self.ui.Nbr_of_point_label.setVisible(True)
        self.ui.Nbr_of_points_spinBox.setVisible(True)
        self.ui.Min_distance_between_steps_label.setVisible(True)
        self.ui.Min_distance_between_steps_lineEdit.setVisible(True)
        self.ui.include_left_edge_as_anchor_label.setVisible(True)
        self.ui.include_left_edge_as_anchor_checkBox.setVisible(True)
        self.ui.include_right_edge_as_anchor_label.setVisible(True)
        self.ui.include_right_edge_as_anchor_checkBox.setVisible(True)
        self.ui.Num_fitpoints_between_1_2_label.setVisible(True)
        self.ui.Num_fitpoints_between_point_1and2_slider.setVisible(True)
        self.ui.Num_fitpoints_between_2_3_label.setVisible(True)
        self.ui.Num_fitpoints_between_point_2and3_slider.setVisible(True)
        self.ui.Num_fitpoints_between_3_4_label.setVisible(True)
        self.ui.Num_fitpoints_between_point_3and4_slider.setVisible(True)
        self.ui.Num_fitpoints_between_4_5_label.setVisible(True)
        self.ui.Num_fitpoints_between_point_4and5_slider.setVisible(True)
        self.ui.Add_anchor_at_Value_label.setVisible(False)
        self.ui.addachoratvalue_horizontalSlider.setVisible(False)
        self.ui.Add_pushButton.setVisible(False)
        self.ui.Undo_pushButton.setVisible(False)
        self.ui.Delete_all_pushButton.setVisible(False)
        self.hide_reveal_slider_row(self.G_fit_num)
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print("Automatic mode UI set")

    def set_manual_mode(self):
        """Set fit mode to manual and update UI visibility."""
        self.G_fit_Mode = self.fit_settings_selection[1]
        print(f"G_fit_Mode set to: {self.G_fit_Mode}")
        self.ui.Find_fitpoints_Automatically_pushButton.setStyleSheet("background-color: none; color: black")
        self.ui.Manually_select_fitpoints_pushButton.setStyleSheet("background-color: green; color: black")
        self.ui.Nbr_of_point_label.setVisible(False)
        self.ui.Nbr_of_points_spinBox.setVisible(False)
        self.ui.Min_distance_between_steps_label.setVisible(False)
        self.ui.Min_distance_between_steps_lineEdit.setVisible(False)
        self.ui.include_left_edge_as_anchor_label.setVisible(False)
        self.ui.include_left_edge_as_anchor_checkBox.setVisible(False)
        self.ui.include_right_edge_as_anchor_label.setVisible(False)
        self.ui.include_right_edge_as_anchor_checkBox.setVisible(False)
        self.ui.Num_fitpoints_between_1_2_label.setVisible(False)
        self.ui.Num_fitpoints_between_point_1and2_slider.setVisible(False)
        self.ui.Num_fitpoints_between_2_3_label.setVisible(False)
        self.ui.Num_fitpoints_between_point_2and3_slider.setVisible(False)
        self.ui.Num_fitpoints_between_3_4_label.setVisible(False)
        self.ui.Num_fitpoints_between_point_3and4_slider.setVisible(False)
        self.ui.Num_fitpoints_between_4_5_label.setVisible(False)
        self.ui.Num_fitpoints_between_point_4and5_slider.setVisible(False)
        self.ui.Add_anchor_at_Value_label.setVisible(True)
        self.ui.addachoratvalue_horizontalSlider.setVisible(True)
        self.ui.Add_pushButton.setVisible(True)
        self.ui.Undo_pushButton.setVisible(True)
        self.ui.Delete_all_pushButton.setVisible(True)
        self.hide_reveal_slider_row(1)
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print("Manual mode UI set")

    def hide_reveal_slider_row(self, num):
        """Show/hide sliders based on number of points."""
        sliders = [
            (self.ui.Num_fitpoints_between_1_2_label, self.ui.Num_fitpoints_between_point_1and2_slider),
            (self.ui.Num_fitpoints_between_2_3_label, self.ui.Num_fitpoints_between_point_2and3_slider),
            (self.ui.Num_fitpoints_between_3_4_label, self.ui.Num_fitpoints_between_point_3and4_slider),
            (self.ui.Num_fitpoints_between_4_5_label, self.ui.Num_fitpoints_between_point_4and5_slider),
        ]
        for i in range(10):
            if i < len(sliders):
                sliders[i][0].setVisible(i < num - 1)
                sliders[i][1].setVisible(i < num - 1)
        print(f"Sliders revealed: {min(num-1, 4)}")

    def update_fit_num(self):
        """Update number of fit points and sliders."""
        self.G_fit_num = self.ui.Nbr_of_points_spinBox.value()
        self.hide_reveal_slider_row(self.G_fit_num)
        self.update_fitpoints()
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print(f"G_fit_num updated to: {self.G_fit_num}")

    def update_fit_min_dist(self, text):
        """Update minimum distance between steps."""
        try:
            self.G_fit_min_dist = float(text)
            self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
            print(f"G_fit_min_dist updated to: {self.G_fit_min_dist}")
        except ValueError:
            print("Invalid Min_distance_between_steps_lineEdit input")

    def update_include_left(self, state):
        """Update include left edge and fit num."""
        self.fit_includeleft = bool(state)
        adjustment = 2 if self.fit_includeleft else -2
        self.ui.Nbr_of_points_spinBox.setValue(self.G_fit_num + adjustment)
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print(f"fit_includeleft updated to: {self.fit_includeleft}, G_fit_num={self.ui.Nbr_of_points_spinBox.value()}")

    def update_include_right(self, state):
        """Update include right edge and fit num."""
        self.fit_includeright = bool(state)
        adjustment = 2 if self.fit_includeright else -2
        self.ui.Nbr_of_points_spinBox.setValue(self.G_fit_num + adjustment)
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print(f"fit_includeright updated to: {self.fit_includeright}, G_fit_num={self.ui.Nbr_of_points_spinBox.value()}")

    def update_fitpoints(self, index=None):
        """Update fitpoints from sliders."""
        sliders = [
            self.ui.Num_fitpoints_between_point_1and2_slider,
            self.ui.Num_fitpoints_between_point_2and3_slider,
            self.ui.Num_fitpoints_between_point_3and4_slider,
            self.ui.Num_fitpoints_between_point_4and5_slider,
        ]
        if index is None:
            self.G_fitpoints = [slider.value() for slider in sliders[:self.G_fit_num-1]]
        else:
            self.G_fitpoints[index-1] = sliders[index-1].value()
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print(f"G_fitpoints updated: {self.G_fitpoints}")

    def add_manual_fitpoint(self):
        """Add manual fitpoint from slider."""
        value = self.ui.addachoratvalue_horizontalSlider.value()
        self.G_manual_fitpoints.append(value)
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print(f"Manual fitpoint added: {value}, G_manual_fitpoints={self.G_manual_fitpoints}")

    def undo_manual_fitpoint(self):
        """Undo last manual fitpoint (placeholder)."""
        print("Undo manual fitpoint (not implemented)")

    def delete_all_manual_fitpoints(self):
        """Delete all manual fitpoints (placeholder)."""
        self.G_manual_fitpoints = []
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print("All manual fitpoints deleted")

    def show_fit_anchor_points(self):
        """Process fitpoints and plot anchor points."""
        if not (self.alignment_tab.cal_imported and self.alignment_tab.data_imported and hasattr(self.alignment_tab, 'best_m') and hasattr(self.alignment_tab, 'best_t')):
            self.ui.Fit_go_pushButton.setStyleSheet("background-color: red; color: black")
            QMessageBox.critical(self.main_window, "Error", 
                                 "First import data with buttons above. Red: This step is missing previous steps. Yellow: This step has not been done. Green: This step has been done")
            print("Error: Alignment not completed")
            return

        X_cal, Y_cal = self.alignment_tab.apply_parameters_to_data(
            self.alignment_tab.X_c, self.alignment_tab.Y_c, self.alignment_tab.borders_cal, self.alignment_tab.cal_is_flipped)
        X_dat, Y_dat = self.alignment_tab.apply_parameters_to_data(
            self.alignment_tab.X_data, self.alignment_tab.Y_data, self.alignment_tab.borders_data, self.alignment_tab.data_is_flipped)
        X_cal = self.alignment_tab.best_m * X_cal + self.alignment_tab.best_t

        if self.G_fit_Mode == self.fit_settings_selection[0]:  # Automatic mode
            X_plateaus_cal, step_pos = self.alignment_tab.estimate_plateaus(X_cal, Y_cal, plot_plateau=False, variable_set="Get Fitpoints")
            Y_plateaus_cal = [Y_cal[self.alignment_tab.get_closest_pxl_to_value(X_cal, i)[0]] for i in X_plateaus_cal]
            print(f"Initial X_plateaus_cal: {X_plateaus_cal}")
            print(f"Initial Y_plateaus_cal: {Y_plateaus_cal}")

            if self.fit_includeleft:
                Y_plateaus_cal.insert(0, Y_cal[0])
                X_plateaus_cal.insert(0, X_cal[0])
            if self.fit_includeright:
                Y_plateaus_cal.append(Y_cal[-1])
                X_plateaus_cal.append(X_cal[-1])
            print(f"Y_plateaus_cal (with edges): {Y_plateaus_cal}")

            k = 0
            for i in range(len(Y_plateaus_cal) - 1):
                if i < len(self.G_fitpoints) and self.G_fitpoints[i] != 0:
                    inbetween_fitpoints = self.G_fitpoints[i]
                    sign_of_step = np.sign(Y_plateaus_cal[i+1+k] - Y_plateaus_cal[i+k])
                    start_of_step = Y_plateaus_cal[i+k]
                    height_of_step = np.abs(Y_plateaus_cal[i+1+k] - Y_plateaus_cal[i+k])
                    for j in range(inbetween_fitpoints):
                        Y_plateaus_cal.insert(i+1+k, start_of_step + (j+1) * sign_of_step * height_of_step / (inbetween_fitpoints + 1))
                        X_plateaus_cal.insert(i+1+k, X_cal[self.alignment_tab.get_closest_pxl_to_value(Y_cal, Y_plateaus_cal[i+1+k])[0]])
                        k += 1
            print(f"Y_plateaus_cal (with fitpoints): {Y_plateaus_cal}")

        else:  # Manual mode
            Y_plateaus_cal = self.G_manual_fitpoints[:]
            print(f"Manual Y_plateaus_cal: {Y_plateaus_cal}")

        if len(Y_plateaus_cal) != len(set(Y_plateaus_cal)):
            QMessageBox.critical(self.main_window, "Error", "Duplicate values detected. Please exclude flat edges and/or reduce number of anchors")
            print("Error: Duplicate Y_plateaus_cal values")
            return

        X_plateaus_cal = [X_cal[self.alignment_tab.get_closest_pxl_to_value(Y_cal, i)[0]] for i in Y_plateaus_cal]
        X_plateaus_dat = [X_dat[self.alignment_tab.get_closest_pxl_to_value(X_dat, i)[0]] for i in X_plateaus_cal]
        Y_plateaus_dat = [Y_dat[self.alignment_tab.get_closest_pxl_to_value(X_dat, i)[0]] for i in X_plateaus_dat]
        print(f"Processed steps: X_plateaus_cal={X_plateaus_cal}, X_plateaus_dat={X_plateaus_dat}, Y_plateaus_cal={Y_plateaus_cal}, Y_plateaus_dat={Y_plateaus_dat}")

        # Interpolate Y_cal to match Y_dat length for scatter plot
        if len(Y_cal) != len(Y_dat):
            x_new = np.linspace(min(X_dat), max(X_dat), len(Y_dat))
            Y_cal_interp = np.interp(x_new, X_cal, Y_cal)
        else:
            Y_cal_interp = Y_cal

        # Plot fit_overlay
        self.figure_fit_overlay.clear()
        ax = self.figure_fit_overlay.add_subplot(111)
        ax.set_title("Anchor Points shown in Calibration Data")
        ax.scatter(Y_cal, X_cal, color='r', marker='x', alpha=0.2)
        ax.set_xlabel("Calibration Data")
        ax.xaxis.label.set_color('red')
        ax.tick_params(axis='x', colors='red')
        ax.set_xlim([np.max(Y_cal) - 1.05 * (np.max(Y_cal) - np.min(Y_cal)), np.max(Y_cal) * 1.05])
        if self.main_window.select_calibration_tab.G_cal_setting == 1:
            ax.invert_xaxis()
        k = 0
        for i in range(len(X_plateaus_cal)):
            if (i == 0 and self.fit_includeleft) or (i == len(X_plateaus_cal) - 1 and self.fit_includeright):
                ax.axvline(Y_plateaus_cal[i], color='r', ls='--', lw=2)
            else:
                ax.axvline(Y_plateaus_cal[i], color='k', ls='--', lw=2)
            if i < len(self.G_fitpoints) and self.G_fitpoints[i] != 0 and i < len(X_plateaus_cal) - 1:
                for _ in range(self.G_fitpoints[i]):
                    k += 1
                    if i + k < len(Y_plateaus_cal):
                        ax.axvline(Y_plateaus_cal[i + k], color='b', ls='--', lw=1)
        self.figure_fit_overlay.tight_layout()
        self.canvas_fit_overlay.draw_idle()

        # Plot fit_overlay2
        self.figure_fit_overlay2.clear()
        ax2 = self.figure_fit_overlay2.add_subplot(111)
        ax2.set_title("Anchor Points shown in Measurement Data")
        ax2.scatter(Y_dat, X_dat, edgecolors='blue', facecolors='white', alpha=0.2, marker='o', s=2)
        ax2.set_xlabel("Measurement Data")
        ax2.xaxis.label.set_color('blue')
        ax2.tick_params(axis='x', colors='blue')
        ax2.set_xlim([np.max(Y_dat) - 1.05 * (np.max(Y_dat) - np.min(Y_dat)), np.max(Y_dat) * 1.05])
        k = 0
        for i in range(len(X_plateaus_dat)):
            if (i == 0 and self.fit_includeleft) or (i == len(X_plateaus_dat) - 1 and self.fit_includeright):
                ax2.axvline(Y_plateaus_dat[i], color='r', ls='--', lw=2)
            else:
                ax2.axvline(Y_plateaus_dat[i], color='k', ls='--', lw=2)
            if i < len(self.G_fitpoints) and self.G_fitpoints[i] != 0 and i < len(X_plateaus_dat) - 1:
                for _ in range(self.G_fitpoints[i]):
                    k += 1
                    if i + k < len(Y_plateaus_dat):
                        ax2.axvline(Y_plateaus_dat[i + k], color='b', ls='--', lw=1)
        self.figure_fit_overlay2.tight_layout()
        self.canvas_fit_overlay2.draw_idle()

        # Plot fit_cal_curve
        self.figure_fit_cal_curve.clear()
        ax3 = self.figure_fit_cal_curve.add_subplot(111)
        ax3.set_title("Calibration Curve with Anchor Points")
        ax3.scatter(np.power(10., Y_dat), np.power(10., Y_cal_interp), color='b', alpha=0.2)
        ax3.set_xlabel("Measurement Data")
        ax3.set_ylabel("Calibration Data")
        k = 0
        for i in range(len(X_plateaus_cal)):
            if (i == 0 and self.fit_includeleft) or (i == len(X_plateaus_cal) - 1 and self.fit_includeright):
                ax3.scatter(np.power(10., Y_plateaus_dat[i]), 
                           np.power(10., Y_plateaus_cal[i]), 
                           marker='*', facecolors='r', s=117, zorder=1)
            else:
                ax3.scatter(np.power(10., Y_plateaus_dat[i]), 
                           np.power(10., Y_plateaus_cal[i]), 
                           marker='*', facecolors='k', s=117, zorder=1)
            if i < len(self.G_fitpoints) and self.G_fitpoints[i] != 0 and i < len(X_plateaus_cal) - 1:
                for _ in range(self.G_fitpoints[i]):
                    k += 1
                    if i + k < len(Y_plateaus_cal):
                        ax3.scatter(np.power(10., Y_plateaus_dat[i + k]), 
                                   np.power(10., Y_plateaus_cal[i + k]), 
                                   marker='*', facecolors='darkblue', s=70, zorder=1)
        self.figure_fit_cal_curve.tight_layout()
        self.canvas_fit_cal_curve.draw_idle()

        self.ui.Fit_go_pushButton.setStyleSheet("background-color: green; color: black")
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print("Anchor points plotted")
        self.Y_plateaus_cal = Y_plateaus_cal
        self.Y_plateaus_dat = Y_plateaus_dat

    def fit_go(self):
        """Finalize fitpoints and plot calibration curves."""
        if not hasattr(self, 'Y_plateaus_cal') or not hasattr(self, 'Y_plateaus_dat'):
            self.ui.Fit_go_pushButton.setStyleSheet("background-color: red; color: black")
            QMessageBox.critical(self.main_window, "Error", 
                                 "First import data with buttons above. Red: This step is missing previous steps. Yellow: This step has not been done. Green: This step has been done")
            print("Error: Anchor points not generated")
            return

        X_cal, Y_cal = self.alignment_tab.apply_parameters_to_data(
            self.alignment_tab.X_c, self.alignment_tab.Y_c, self.alignment_tab.borders_cal, self.alignment_tab.cal_is_flipped)
        X_dat, Y_dat = self.alignment_tab.apply_parameters_to_data(
            self.alignment_tab.X_data, self.alignment_tab.Y_data, self.alignment_tab.borders_data, self.alignment_tab.data_is_flipped)
        X_cal = self.alignment_tab.best_m * X_cal + self.alignment_tab.best_t

        # Interpolate Y_cal to match Y_dat length for scatter plot
        if len(Y_cal) != len(Y_dat):
            x_new = np.linspace(min(X_dat), max(X_dat), len(Y_dat))
            Y_cal_interp = np.interp(x_new, X_cal, Y_cal)
        else:
            Y_cal_interp = Y_cal

        Y_plateaus_cal = self.Y_plateaus_cal
        Y_plateaus_dat = self.Y_plateaus_dat
        X_plateaus_cal = [X_cal[self.alignment_tab.get_closest_pxl_to_value(Y_cal, i)[0]] for i in Y_plateaus_cal]
        X_plateaus_dat = [X_dat[self.alignment_tab.get_closest_pxl_to_value(X_dat, i)[0]] for i in X_plateaus_cal]

        # Sort plateaus
        G_cal_setting = self.main_window.select_calibration_tab.G_cal_setting
        if G_cal_setting == 1:
            plateau_order = sorted(range(len(Y_plateaus_cal)), key=lambda k: Y_plateaus_cal[k])[::-1]
        else:
            plateau_order = sorted(range(len(Y_plateaus_cal)), key=lambda k: Y_plateaus_cal[k])
        X_plateaus_cal = [X_plateaus_cal[i] for i in plateau_order]
        X_plateaus_dat = [X_plateaus_dat[i] for i in plateau_order]
        Y_plateaus_cal = [Y_plateaus_cal[i] for i in plateau_order]
        Y_plateaus_dat = [Y_plateaus_dat[i] for i in plateau_order]
        print(f"Ordered steps: X_plateaus_cal={X_plateaus_cal}, X_plateaus_dat={X_plateaus_dat}, Y_plateaus_cal={Y_plateaus_cal}, Y_plateaus_dat={Y_plateaus_dat}")

        # Compute initial guess
        initialguess = []
        for i in range(len(Y_plateaus_dat)):
            if i == 0:
                initialguess.append(Y_plateaus_dat[i])
            else:
                initialguess.append(Y_plateaus_dat[i] - Y_plateaus_dat[i-1])
        print(f"Initial guess: {initialguess}")

        # Linear interpolation
        def make_func(x_values):
            def interpolation(x, *args):
                return np.interp(x, x_values, args)
            return interpolation, interpolation
        interpolation, _ = make_func(Y_plateaus_cal)
        Y_dat_initialguess_calibrated = interpolation(X_dat, *Y_plateaus_dat)

        # Plot calibration overlay
        self.figure_fit_overlay.clear()
        ax = self.figure_fit_overlay.add_subplot(111)
        ax.set_title("Calibration Overlay")
        ax.plot(X_cal, Y_cal, color='r', label='Calibration')
        ax.plot(X_dat, Y_dat_initialguess_calibrated, color='b', label='Calibrated Measurement')
        ax.set_xlabel("Depth [mm]")
        ax.set_ylabel("Calibration Data")
        ax.yaxis.label.set_color('red')
        ax.tick_params(axis='y', colors='red')
        ax.set_ylim([np.max(Y_cal) - 1.05 * (np.max(Y_cal) - np.min(Y_cal)), np.max(Y_cal) * 1.05])
        ax2 = ax.twinx()
        ax2.set_ylabel("Measurement Data")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.set_ylim([np.max(Y_dat_initialguess_calibrated) - 1.05 * (np.max(Y_dat_initialguess_calibrated) - np.min(Y_dat_initialguess_calibrated)), 
                      np.max(Y_dat_initialguess_calibrated) * 1.05])
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        self.figure_fit_overlay.tight_layout()
        self.canvas_fit_overlay.draw_idle()

        # Plot calibration curve
        self.figure_fit_cal_curve.clear()
        ax3 = self.figure_fit_cal_curve.add_subplot(111)
        ax3.set_title("Calibration Curve")
        ax3.scatter(np.power(10., Y_dat), np.power(10., Y_cal_interp), color='b', alpha=0.2)
        k = 0
        for i in range(len(X_plateaus_cal)):
            if (i == 0 and self.fit_includeleft) or (i == len(X_plateaus_cal) - 1 and self.fit_includeright):
                ax3.scatter(np.power(10., Y_plateaus_dat[i]), 
                           np.power(10., Y_plateaus_cal[i]), 
                           marker='*', facecolors='r', s=117, zorder=1)
            else:
                ax3.scatter(np.power(10., Y_plateaus_dat[i]), 
                           np.power(10., Y_plateaus_cal[i]), 
                           marker='*', facecolors='k', s=117, zorder=1)
            if i < len(self.G_fitpoints) and self.G_fitpoints[i] != 0 and i < len(X_plateaus_cal) - 1:
                for _ in range(self.G_fitpoints[i]):
                    k += 1
                    if i + k < len(Y_plateaus_cal):
                        ax3.scatter(np.power(10., Y_plateaus_dat[i + k]), 
                                   np.power(10., Y_plateaus_cal[i + k]), 
                                   marker='*', facecolors='darkblue', s=70, zorder=1)
        self.figure_fit_cal_curve.tight_layout()
        self.canvas_fit_cal_curve.draw_idle()

        self.ui.Fit_go_pushButton.setStyleSheet("background-color: green; color: black")
        print("Calibration curves plotted")