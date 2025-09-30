from PyQt5.QtWidgets import QMessageBox, QVBoxLayout
from PyQt5.QtCore import Qt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from app.select_calibration_tab import preset_lib

class FitpointsTab:
    """Controller for the 'Fitpoints' tab functionality."""
    def __init__(self, ui, main_window):
        """Initialize the tab with UI elements and data attributes."""
        self.ui = ui
        self.main_window = main_window
        self.alignment_tab = main_window.alignment_tab
        self.select_calibration_tab = main_window.select_calibration_tab
        self.import_measurement_tab = main_window.import_measurement_tab
        #self.calibration_tab = main_window.calibration_tab
        #self.calibration_tab= main_window.calibration_tab

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
        G_u =1E6

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

        #self.figure_calibration_overlay = Figure(figsize=self.G_canvas_aspect_ratio*1.5/self.G_canvas_dpi, dpi=self.G_canvas_dpi)
        #self.canvas_calibration_overlay = FigureCanvas(self.figure_calibration_overlay)
        #try:
        #    self.ui.fit_cal_curve_verticalLayout.addWidget(self.canvas_calibration_overlay)
        #    print("Calibration overlay canvas added to calibration_overlay_verticalLayout")
        #except AttributeError as e:
        #    print(f"Error: {e}. Ensure calibration_overlay_verticalLayout exists.")
        #    raise SystemExit(1)

        # Connect buttons
        try:
            self.ui.Find_fitpoints_Automatically_pushButton.clicked.connect(self.set_auto_mode)
            self.ui.Manually_select_fitpoints_pushButton.clicked.connect(self.set_manual_mode)
            self.ui.Add_pushButton.clicked.connect(self.add_manual_fitpoint)
            self.ui.Undo_pushButton.clicked.connect(self.undo_manual_fitpoint)
            self.ui.Delete_all_pushButton.clicked.connect(self.delete_all_manual_fitpoints)
            self.ui.Fit_go_pushButton.clicked.connect(self.show_fit_anchor_points)
            print("Button signals connected")
        except AttributeError as e:
            print(f"Error: {e}. Ensure all buttons exist in UI.")
            raise SystemExit(1)

        # Connect spinbox, line edit, checkboxes, and sliders
        try:
            self.ui.Nbr_of_points_spinBox.valueChanged.connect(self.update_fit_num)
            self.ui.Min_distance_between_steps_lineEdit.textChanged.connect(self.update_fit_min_dist)
            self.ui.include_left_edge_as_anchor_checkBox.stateChanged.connect(self.update_include_left)
            self.ui.include_right_edge_as_anchor_checkBox.stateChanged.connect(self.update_include_right)
            #self.ui.Num_fitpoints_between_point_1and2_slider.valueChanged.connect(lambda: self.update_fitpoints(1))
            #self.ui.Num_fitpoints_between_point_2and3_slider.valueChanged.connect(lambda: self.update_fitpoints(2))
            #self.ui.Num_fitpoints_between_point_3and4_slider.valueChanged.connect(lambda: self.update_fitpoints(3))
            #self.ui.Num_fitpoints_between_point_4and5_slider.valueChanged.connect(lambda: self.update_fitpoints(4))
            self.select_calibration_tab.ui.calib_sample_combobox.currentTextChanged.connect(self.update_from_preset)
            print("SpinBox, LineEdit, CheckBox, Slider, and Combobox signals connected")
        except AttributeError as e:
            print(f"Error: {e}. Ensure UI elements exist.")
            raise SystemExit(1)
        
                # Connect sliders
        self.sliders = [
            self.ui.Num_fitpoints_between_point_1and2_slider,
            self.ui.Num_fitpoints_between_point_2and3_slider,
            self.ui.Num_fitpoints_between_point_3and4_slider,
            self.ui.Num_fitpoints_between_point_4and5_slider,
            self.ui.Num_fitpoints_between_point_5and6_slider,
            self.ui.Num_fitpoints_between_point_6and7_slider,
            self.ui.Num_fitpoints_between_point_7and8_slider,
            self.ui.Num_fitpoints_between_point_8and9_slider,
            self.ui.Num_fitpoints_between_point_9and10_slider
        ]
        # Configure sliders: range [0, 4], step 1
        for slider in self.sliders:
            slider.setMinimum(0)
            slider.setMaximum(4)
            slider.setSingleStep(1)
            slider.valueChanged.connect(self.update_fitpoints)

        # Configure Nbr_of_points_spinBox: max 10
        self.ui.Nbr_of_points_spinBox.setMaximum(10)
        self.ui.Nbr_of_points_spinBox.setMinimum(2)
                
        # Initialize UI visibility
        self.set_auto_mode()
        self.update_from_preset(self.select_calibration_tab.ui.calib_sample_combobox.currentText())

    
    def reset_show_Fit_anchor_button_state(self):
        """Reset measurement import state and update button colors."""
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        

    def update_from_preset(self, cal_name):
        """Update fit parameters from preset_lib based on selected calibration sample."""
        preset_key = "Charge carriers -- default" if self.select_calibration_tab.G_cal_setting == 1 else "Resistivity -- default"
        preset = preset_lib.get(cal_name, {}).get(preset_key, {})
        self.G_fit_num = preset.get("-num_steps-", 5)
        self.G_fit_min_dist = preset.get("-step_distance-", 1)
        self.G_fitpoints = preset.get("-fitpoints-", [0] * (self.G_fit_num - 1))
        self.ui.Nbr_of_points_spinBox.setValue(self.G_fit_num)
        self.ui.Min_distance_between_steps_lineEdit.setText(str(self.G_fit_min_dist))
        self.hide_reveal_slider_row(self.G_fit_num)
        self.update_fitpoints()
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print(f"Updated from preset: cal_name={cal_name}, G_fit_num={self.G_fit_num}, G_fit_min_dist={self.G_fit_min_dist}, G_fitpoints={self.G_fitpoints}")

    def set_auto_mode(self):
        """Set automatic fit mode and show sliders."""
        self.G_fit_Mode = self.fit_settings_selection[0]
        self.ui.Min_distance_between_steps_lineEdit.setVisible(True)
        self.ui.Nbr_of_points_spinBox.setVisible(True)
        self.ui.include_left_edge_as_anchor_checkBox.setVisible(True)
        self.ui.include_right_edge_as_anchor_checkBox.setVisible(True)
        self.ui.Add_pushButton.setVisible(False)
        self.ui.Undo_pushButton.setVisible(False)
        self.ui.Delete_all_pushButton.setVisible(False)
        self.hide_reveal_slider_row(self.G_fit_num)
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print("PyQt - Switched to automatic mode")

    def set_manual_mode(self):
        """Set manual fit mode and hide sliders."""
        self.G_fit_Mode = self.fit_settings_selection[1]
        self.ui.Min_distance_between_steps_lineEdit.setVisible(False)
        self.ui.Nbr_of_points_spinBox.setVisible(False)
        self.ui.include_left_edge_as_anchor_checkBox.setVisible(False)
        self.ui.include_right_edge_as_anchor_checkBox.setVisible(False)
        self.ui.Add_pushButton.setVisible(True)
        self.ui.Undo_pushButton.setVisible(True)
        self.ui.Delete_all_pushButton.setVisible(True)
        self.hide_reveal_slider_row(1)  # Hide all sliders
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print("PyQt - Switched to manual mode")

    def hide_reveal_slider_row(self, num):
        """Show/hide sliders based on num - 1, up to available sliders."""
        max_sliders = len(self.sliders)  # 4 sliders from Qt Designer
        for i in range(max_sliders):
            self.sliders[i].setVisible(False)
            self.ui.__dict__[f"label_{i+1}_and_{i+2}"].setVisible(False)  # Assumes labels named label_1_and_2, etc.
        for i in range(min(num - 1, max_sliders)):
            self.sliders[i].setVisible(True)
            self.ui.__dict__[f"label_{i+1}_and_{i+2}"].setVisible(True)
        # Warn if G_fit_num exceeds available sliders
        if num - 1 > max_sliders:
            print(f"PyQt - Warning: G_fit_num={num} requires {num-1} sliders, but only {max_sliders} available")

    def update_fit_num(self):
        """Update number of fit points and sliders."""
        self.G_fit_num = self.ui.Nbr_of_points_spinBox.value()
        # Resize G_fitpoints to match G_fit_num - 1, using slider values if available
        max_sliders = len(self.sliders)
        self.G_fitpoints = [self.sliders[i].value() if i < max_sliders else 0 for i in range(self.G_fit_num - 1)]
        self.hide_reveal_slider_row(self.G_fit_num)
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        #self.show_fit_anchor_points()
        print(f"PyQt - G_fit_num updated to: {self.G_fit_num}, G_fitpoints={self.G_fitpoints}")

    def update_fit_min_dist(self, text):
        """Update minimum distance between steps."""
        try:
            self.G_fit_min_dist = float(text)
            self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
            print(f"G_fit_min_dist updated to: {self.G_fit_min_dist}")
        except ValueError:
            print("Invalid Min_distance_between_steps_lineEdit input")

    def update_include_left(self):
        """Update include left edge setting and adjust number of fit points."""
        self.fit_includeleft = self.ui.include_left_edge_as_anchor_checkBox.isChecked()
        # Update G_fit_num first, then set spinbox
        self.G_fit_num = self.ui.Nbr_of_points_spinBox.value()
        new_value = self.G_fit_num + int(self.fit_includeleft) * 2 - 1
        self.ui.Nbr_of_points_spinBox.setValue(new_value)
        self.G_fit_num = new_value  # Sync G_fit_num with spinbox
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        self.show_fit_anchor_points()
        print(f"PyQt - fit_includeleft: {self.fit_includeleft}, G_fit_num: {self.G_fit_num}")
    
    def update_include_right(self):
        """Update include right edge setting and adjust number of fit points."""
        self.fit_includeright = self.ui.include_right_edge_as_anchor_checkBox.isChecked()
        # Update G_fit_num first, then set spinbox
        self.G_fit_num = self.ui.Nbr_of_points_spinBox.value()
        new_value = self.G_fit_num + int(self.fit_includeright) * 2 - 1
        self.ui.Nbr_of_points_spinBox.setValue(new_value)
        self.G_fit_num = new_value  # Sync G_fit_num with spinbox
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        self.show_fit_anchor_points()
        print(f"PyQt - fit_includeright: {self.fit_includeright}, G_fit_num: {self.G_fit_num}")

    def update_fitpoints(self):
        """Update G_fitpoints from slider values."""
        max_sliders = len(self.sliders)
        self.G_fitpoints = [self.sliders[i].value() if i < min(self.G_fit_num - 1, max_sliders) else 0 for i in range(self.G_fit_num - 1)]
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        #self.show_fit_anchor_points()
        print(f"PyQt - G_fitpoints updated: {self.G_fitpoints}")

    def add_manual_fitpoint(self):
        """Add manual fitpoint from line edit."""
        try:
          #  value = float(self.ui.Add_anchor_at_Value_lineEdit.text())
           # self.G_manual_fitpoints.append(value)
            self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
          #  print(f"Manual fitpoint added: {value}, G_manual_fitpoints={self.G_manual_fitpoints}")
        except ValueError:
            print("Invalid manual fitpoint input")

    def undo_manual_fitpoint(self):
        """Undo last manual fitpoint."""
        if self.G_manual_fitpoints:
            self.G_manual_fitpoints.pop()
            self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
            print(f"Last manual fitpoint removed: G_manual_fitpoints={self.G_manual_fitpoints}")
        else:
            print("No manual fitpoints to undo")

    def delete_all_manual_fitpoints(self):
        """Delete all manual fitpoints."""
        self.G_manual_fitpoints = []
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: yellow; color: black")
        print("All manual fitpoints deleted")


    def draw_xlabel(self, Quantity="Depth", is_log=False):
        """Set x-axis label."""
        ax = self.main_window.calibration_tab.figure_calibration_curve.gca() if self.main_window.calibration_tab.figure_calibration_curve.axes else self.main_window.calibration_tab.figure_calibration_curve.gca()
        if Quantity == "Depth":
            ax.set_xlabel("Depth [mm]")
            #print("X label set to Depth [mm]")
        else:
            label = 'SSRM measured resistance' if self.main_window.import_measurement_tab.G_dat_datatype == "SSRM" else self.main_window.import_measurement_tab.G_dat_denomination
            if is_log and self.G_dat_datatype == "SSRM":
                label += ' [$log_{10}(\Omega)$]'
            elif self.main_window.import_measurement_tab.G_dat_datatype == "SSRM":
                label += ' [$\Omega$]'
            ax.set_xlabel(label, fontsize=10)
            ax.tick_params(axis='both', which='major', labelsize=10)
            ax.tick_params(axis='both', which='minor', labelsize=10)

    def draw_ylabel(self, Quantity="Calibration", is_log=True, figure=None):
        """Set y-axis label for the specified figure."""
        # Use provided figure or default to figure_preview
        figure = figure or self.figure_preview
        ax = figure.gca()
        if Quantity == "Calibration":
            if self.main_window.select_calibration_tab.G_cal_setting == 1:
                # Use p-type or n-type based on G_carrier_type
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
            label = "SSRM measured resistance" if self.G_dat_datatype == "SSRM" else self.import_measurement_tab.G_dat_denomination
            if is_log and self.G_dat_datatype == "SSRM":
                label += " [$log_{10}(\Omega)$]"
            elif self.G_dat_datatype == "SSRM":
                label += " [$\Omega$]"
        ax.set_ylabel(label, fontsize=10)
        print(f"Y label set to {label}")

    def draw_grid(self, ax):
        """Add grid to the plot."""
        ax.grid(color='b', which='minor', linestyle='-.', linewidth=0.25)
        ax.grid(color='b', which='major', linestyle='-.', linewidth=0.5)

    def redraw_calibration_curve_init(self, ax, X_cal, Y_cal, Y_plateaus_dat, Y_plateaus_cal, mode="Calibration"):
            """Initialize calibration curve plot."""

            if mode == "Calibration":
                ax.plot(np.power(10., Y_plateaus_dat), np.power(10., Y_plateaus_cal), color='blue', label='calibration (initial guess)', zorder=0)
            ax.scatter(np.power(10.,self.alignment_tab.ref(X_cal)), np.power(10., Y_cal), color='blue', alpha=0.25, label='Datapoints')
            #self.draw_xlabel()
            #self.draw_ylabel(ax, quantity="Calibration", is_log=False)
            self.draw_grid(ax)
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.legend(loc='best', fontsize=10)


    def show_fit_anchor_points(self):
        """Process fitpoints and plot anchor points for calibration, measurement, and calibration curve."""
        if not (self.alignment_tab.cal_imported and self.alignment_tab.data_imported and 
                hasattr(self.alignment_tab, 'best_m') and hasattr(self.alignment_tab, 'best_t')):
            self.ui.Fit_go_pushButton.setStyleSheet("background-color: red; color: black")
            QMessageBox.critical(self.main_window, "Error", 
                                 "First import data and complete alignment. Red: Missing steps. Yellow: Not done. Green: Done")
            print("Error: Alignment not completed")
            return
        
        # Get preprocessed data
        X_cal, Y_cal = self.alignment_tab.apply_parameters_to_data(
            self.alignment_tab.X_c, self.alignment_tab.Y_c, self.alignment_tab.borders_cal, self.alignment_tab.cal_is_flipped)
        X_dat, Y_dat = self.alignment_tab.apply_parameters_to_data(
            self.alignment_tab.X_data, self.alignment_tab.Y_data, self.alignment_tab.borders_data, self.alignment_tab.data_is_flipped)
        
        # Apply alignment transformation
        X_cal, Y_cal, X_dat, Y_dat = self.alignment_tab.apply_lin_offset(X_cal, Y_cal, X_dat, Y_dat, self.alignment_tab.best_m, self.alignment_tab.best_t)
        print(f"PyQt - show_fit_anchor_points: X_cal after alignment min={np.min(X_cal):.3f}, max={np.max(X_cal):.3f}, len={len(X_cal)}")
        print(f"PyQt - show_fit_anchor_points: X_dat after alignment min={np.min(X_dat):.3f}, max={np.max(X_dat):.3f}, len={len(X_dat)}")
        
        if self.G_fit_Mode == self.fit_settings_selection[0]:  # Automatic mode
            X_plateaus_cal, step_pos = self.alignment_tab.estimate_plateaus(X_cal, Y_cal, plot_plateau=False, variable_set="Get Fitpoints")
            Y_plateaus_cal = [Y_cal[self.alignment_tab.get_closest_pxl_to_value(X_cal, i)[0]] for i in X_plateaus_cal]
            print(f"PyQt - Initial X_plateaus_cal: {X_plateaus_cal}")
            print(f"PyQt - Initial Y_plateaus_cal: {Y_plateaus_cal}")
            if self.fit_includeleft:
                Y_plateaus_cal.insert(0, Y_cal[0])
                X_plateaus_cal.insert(0, X_cal[0])
            if self.fit_includeright:
                Y_plateaus_cal.append(Y_cal[-1])
                X_plateaus_cal.append(X_cal[-1])
            # Add intermediate fitpoints
            k = 0
            for i in range(len(X_plateaus_cal) - 1):
                if i < len(self.G_fitpoints) and self.G_fitpoints[i] != 0:
                    inbetween_fitpoints = self.G_fitpoints[i]
                    sign_of_step = np.sign(Y_plateaus_cal[i+1+k] - Y_plateaus_cal[i+k])
                    start_of_step = Y_plateaus_cal[i+k]
                    height_of_step = np.abs(Y_plateaus_cal[i+1+k] - Y_plateaus_cal[i+k])
                    for j in range(inbetween_fitpoints):
                        Y_plateaus_cal.insert(i+1+k, start_of_step + (j+1) * sign_of_step * height_of_step / (inbetween_fitpoints + 1))
                        X_plateaus_cal.insert(i+1+k, X_cal[self.alignment_tab.get_closest_pxl_to_value(Y_cal, Y_plateaus_cal[i+1+k])[0]])
                        k += 1
        else:  # Manual mode
            if not hasattr(self, 'X_plateaus_cal') or not hasattr(self, 'Y_plateaus_cal'):
                print("Error: Manual fitpoints not set. Using empty lists.")
                self.X_plateaus_cal = []
                self.Y_plateaus_cal = []
            X_plateaus_cal = self.X_plateaus_cal
            Y_plateaus_cal = self.Y_plateaus_cal
        print(f"PyQt - Y_plateaus_cal (final): {Y_plateaus_cal}")
        
        # Map calibration plateaus to measurement data
        X_plateaus_cal = [X_cal[self.alignment_tab.get_closest_pxl_to_value(Y_cal, i)[0]] for i in Y_plateaus_cal]
        X_plateaus_dat = [X_dat[self.alignment_tab.get_closest_pxl_to_value(X_dat, i)[0]] for i in X_plateaus_cal]
        Y_plateaus_dat = [Y_dat[self.alignment_tab.get_closest_pxl_to_value(X_dat, i)[0]] for i in X_plateaus_dat]
        print(f"PyQt - Y_plateaus_dat: {Y_plateaus_dat}")
        
        # Store plateaus as class attributes for fit_go
        self.X_plateaus_cal = X_plateaus_cal
        self.Y_plateaus_cal = Y_plateaus_cal
        self.X_plateaus_dat = X_plateaus_dat
        self.Y_plateaus_dat = Y_plateaus_dat
        
        # Ensure G_fitpoints matches G_fit_num - 1
        if len(self.G_fitpoints) < self.G_fit_num - 1:
            self.G_fitpoints.extend([0] * (self.G_fit_num - 1 - len(self.G_fitpoints)))
        elif len(self.G_fitpoints) > self.G_fit_num - 1:
            self.G_fitpoints = self.G_fitpoints[:self.G_fit_num - 1]
        print(f"PyQt - G_fit_num: {self.G_fit_num}")
        print(f"PyQt - G_fitpoints: {self.G_fitpoints}")
        print(f"PyQt - fit_includeleft: {self.fit_includeleft}, fit_includeright: {self.fit_includeright}")
        
        # Plot fit_overlay (calibration data)
        self.figure_fit_overlay.clear()
        ax = self.figure_fit_overlay.add_subplot(111)
        ax.set_title("Anchor Points in Calibration Data")
        ax.scatter(Y_cal, X_cal, color='r', marker='x', alpha=0.2)
        ax.set_xlabel("calibration data")
        ax.xaxis.label.set_color('red')
        ax.tick_params(axis='x', colors='red')
        ax.set_ylim([np.min(X_dat), np.max(X_dat)])
        ax.set_xlim([np.max(Y_cal) - 1.05 * (np.max(Y_cal) - np.min(Y_cal)), np.max(Y_cal) * 1.05])
        
        black_line_positions_cal = []
        num_points = min(self.G_fit_num, len(Y_plateaus_cal))  # Cap at available plateaus
        for i in range(num_points):
            if (i == 0 and self.fit_includeleft) or (i == num_points - 1 and self.fit_includeright):
                if i == 0:
                    ax.axvline(Y_plateaus_cal[0], color='r', ls='--', lw=2)
                    print(f"PyQt - Red line (left edge, cal): {Y_plateaus_cal[0]:.3f}")
                else:
                    ax.axvline(Y_plateaus_cal[-1], color='r', ls='--', lw=2)
                    print(f"PyQt - Red line (right edge, cal): {Y_plateaus_cal[-1]:.3f}")
            else:
                idx = i + sum(self.G_fitpoints[:i])
                if idx < len(Y_plateaus_cal):
                    ax.axvline(Y_plateaus_cal[idx], color='k', ls='--', lw=2)
                    black_line_positions_cal.append(Y_plateaus_cal[idx])
            if i < num_points - 1 and i < len(self.G_fitpoints):
                for k in range(self.G_fitpoints[i]):
                    idx = i + sum(self.G_fitpoints[:i]) + (k + 1)
                    if idx < len(Y_plateaus_cal):
                        ax.axvline(Y_plateaus_cal[idx], color='b', ls='--', lw=1)
                        print(f"PyQt - Blue line (cal, i={i}, k={k}): {Y_plateaus_cal[idx]:.3f}")
        print(f"PyQt - Black line positions (cal): {black_line_positions_cal}")
        
        self.figure_fit_overlay.tight_layout()
        self.canvas_fit_overlay.draw_idle()
        
        # Plot fit_overlay2 (measurement data)
        self.figure_fit_overlay2.clear()
        ax2 = self.figure_fit_overlay2.add_subplot(111)
        ax2.set_title("Anchor Points shown in Measurement Data")
        ax2.scatter(Y_dat, X_dat, edgecolors='blue', facecolors='white', alpha=0.2, marker='o', s=2)
        ax2.set_xlabel("measurement data")
        ax2.xaxis.label.set_color('blue')
        ax2.tick_params(axis='x', colors='blue')
        ax2.set_xlim([np.max(Y_dat) - 1.05 * (np.max(Y_dat) - np.min(Y_dat)), np.max(Y_dat) * 1.05])
        ax2.set_ylim([np.min(X_dat), np.max(X_dat)])
        
        black_line_positions_dat = []
        for i in range(num_points):
            if (i == 0 and self.fit_includeleft) or (i == num_points - 1 and self.fit_includeright):
                if i == 0:
                    ax2.axvline(Y_plateaus_dat[0], color='r', ls='--', lw=2)
                    print(f"PyQt - Red line (left edge, dat): {Y_plateaus_dat[0]:.3f}")
                else:
                    ax2.axvline(Y_plateaus_dat[-1], color='r', ls='--', lw=2)
                    print(f"PyQt - Red line (right edge, dat): {Y_plateaus_dat[-1]:.3f}")
            else:
                idx = i + sum(self.G_fitpoints[:i])
                if idx < len(Y_plateaus_dat):
                    ax2.axvline(Y_plateaus_dat[idx], color='k', ls='--', lw=2)
                    black_line_positions_dat.append(Y_plateaus_dat[idx])
            if i < num_points - 1 and i < len(self.G_fitpoints):
                for k in range(self.G_fitpoints[i]):
                    idx = i + sum(self.G_fitpoints[:i]) + (k + 1)
                    if idx < len(Y_plateaus_dat):
                        ax2.axvline(Y_plateaus_dat[idx], color='b', ls='--', lw=1)
                        print(f"PyQt - Blue line (dat, i={i}, k={k}): {Y_plateaus_dat[idx]:.3f}")
        print(f"PyQt - Black line positions (dat): {black_line_positions_dat}")
        
        #if self.select_calibration_tab.G_cal_setting == 1:
        #    ax2.invert_xaxis()
        
        self.figure_fit_overlay2.tight_layout()
        self.canvas_fit_overlay2.draw_idle()
        print("PyQt - Fit overlay2 plot drawn")
        
        # Plot fit_cal_curve (calibration curve)
        self.figure_fit_cal_curve.clear()
        ax3 = self.figure_fit_cal_curve.add_subplot(111)
        self.redraw_calibration_curve_init(ax3, X_cal, Y_cal, Y_plateaus_dat, Y_plateaus_cal, mode="Anchor_prev")
        
        black_line_positions_curve = []
        for i in range(num_points):
            idx = i + sum(self.G_fitpoints[:i])
            if idx < len(Y_plateaus_cal):
                if (i == 0 and self.fit_includeleft) or (i == num_points - 1 and self.fit_includeright):
                    if i == 0:
                        ax3.scatter(np.power(10., Y_plateaus_dat[0]), np.power(10., Y_plateaus_cal[0]), marker='*', color='r', s=117, zorder=1)
                        print(f"PyQt - Red star (left edge, curve): x={np.power(10., Y_plateaus_dat[0]):.3f}, y={np.power(10., Y_plateaus_cal[0]):.3f}")
                    else:
                        ax3.scatter(np.power(10., Y_plateaus_dat[-1]), np.power(10., Y_plateaus_cal[-1]), marker='*', color='r', s=117, zorder=1)
                        print(f"PyQt - Red star (right edge, curve): x={np.power(10., Y_plateaus_dat[-1]):.3f}, y={np.power(10., Y_plateaus_cal[-1]):.3f}")
                else:
                    ax3.scatter(np.power(10., Y_plateaus_dat[idx]), np.power(10., Y_plateaus_cal[idx]), marker='*', color='k', s=117, zorder=1)
                    black_line_positions_curve.append((np.power(10., Y_plateaus_dat[idx]), np.power(10., Y_plateaus_cal[idx])))
            if i < num_points - 1 and i < len(self.G_fitpoints):
                for k in range(self.G_fitpoints[i]):
                    idx = i + sum(self.G_fitpoints[:i]) + (k + 1)
                    if idx < len(Y_plateaus_cal):
                        ax3.scatter(np.power(10., Y_plateaus_dat[idx]), np.power(10., Y_plateaus_cal[idx]), marker='*', color='darkblue', s=70, zorder=1)
                        print(f"PyQt - Dark blue star (curve, i={i}, k={k}): x={np.power(10., Y_plateaus_dat[idx]):.3f}, y={np.power(10., Y_plateaus_cal[idx]):.3f}")
        print(f"PyQt - Black star positions (curve): {black_line_positions_curve}")
        
        self.draw_ylabel(Quantity="Calibration", is_log=not self.main_window.select_calibration_tab.scale_cal_data, figure=self.figure_fit_cal_curve)
        self.draw_xlabel(Quantity="Data",is_log=False)
        self.figure_fit_cal_curve.tight_layout()
        self.canvas_fit_cal_curve.draw_idle()
        print("PyQt - Fit cal curve plot drawn")
        
        # Call fit_go to plot calibration tab figures
        self.fit_go()
        
    

    def make_func(self,Dopants):
        def _function_linint_(R,*args):
            # only monotone changes allowed (so far) --> check whether the data suggest a falling profile or a rising one
            sign_data = np.sign(np.sum(args[1:]))
            G_u = 1E6
            def halfstep_l(x,val):
                return 0.5*(1+np.tanh(-G_u*(x-val)))
            def halfstep_r(x,val):
                return 0.5*(1+np.tanh(G_u*(x-val)))
            def step(x,val_l,val_r):
                return 0.5*(np.tanh(G_u*(x-val_l))-np.tanh(G_u*(x-val_r)))
            def interval(x,val_l,val_r,D_l,D_r):
                return ((x-val_l)*(D_r-D_l)/(val_r-val_l)+D_l)*step(x,val_l,val_r)
            # build resistance values along axis (only positive changes allowed / go from low r to high r)
            r = []
            j = 0
            for i in args:
                if j is not 0:
                    i = j +sign_data*abs(i)
                j = i
                r.append(i)
    
            # list of segments (each segment will be an array)
            y = []
            for i in range(0,len(r)-1): # segments are between two points r. Thus one pixel smaller
                if i==0:#first segment for extrapolation to lower r vals
                    if sign_data==-1:
                        y.append(((R-r[i+1])*(Dopants[i+1]-Dopants[i])/(r[i+1]-r[i])+Dopants[1])*halfstep_r(R,r[i+1]))
                    elif sign_data==1:
                        y.append(((R-r[i+1])*(Dopants[i+1]-Dopants[i])/(r[i+1]-r[i])+Dopants[1])*halfstep_l(R,r[i+1]))
    
                elif i==(len(r)-2): #last segment for extrapolation to higher r vals 
                    if sign_data==-1:
                        y.append(((R-r[i])*(Dopants[i+1]-Dopants[i])/(r[i+1]-r[i])+Dopants[i])*halfstep_l(R,r[i]))
                    elif sign_data==1:
                        y.append(((R-r[i])*(Dopants[i+1]-Dopants[i])/(r[i+1]-r[i])+Dopants[i])*halfstep_r(R,r[i]))
    
                else: # interpolation
                    if sign_data==1:
                        y.append(interval(R,r[i],r[i+1],Dopants[i],Dopants[i+1]))
                    elif sign_data==-1:
                        y.append(-interval(R,r[i],r[i+1],Dopants[i],Dopants[i+1]))
    
            return  np.sum(np.array(y),axis=0)  # convert to array, sum over axis to combine all segments into on function
        

        def _function_main(X, *args):
            ref_X_dat = self.alignment_tab.ref(X)

            print(f"PyQt - calibration_start: ref_X_dat min={np.min(ref_X_dat):.3f}, max={np.max(ref_X_dat):.3f}, len={len(ref_X_dat)}")

            return _function_linint_(self.alignment_tab.ref(X), *args)
            
        return _function_main,_function_linint_
    
    def fit_go(self):
        """Finalize fitpoints and plot calibration curves."""
        if not hasattr(self, 'Y_plateaus_cal') or not hasattr(self, 'Y_plateaus_dat'):
            self.ui.Fit_go_pushButton.setStyleSheet("background-color: red; color: black")
            QMessageBox.critical(self.main_window, "Error", 
                                 "First generate anchor points. Red: Missing steps. Yellow: Not done. Green: Done")
            print("Error: Anchor points not generated")
            return
    
        X_cal, Y_cal = self.alignment_tab.apply_parameters_to_data(
            self.alignment_tab.X_c, self.alignment_tab.Y_c, self.alignment_tab.borders_cal, self.alignment_tab.cal_is_flipped)
        X_dat, Y_dat = self.alignment_tab.apply_parameters_to_data(
            self.alignment_tab.X_data, self.alignment_tab.Y_data, self.alignment_tab.borders_data, self.alignment_tab.data_is_flipped)
        X_cal, Y_cal, X_dat, Y_dat = self.alignment_tab.apply_lin_offset(X_cal, Y_cal, X_dat, Y_dat, self.alignment_tab.best_m, self.alignment_tab.best_t)
        print(f"PyQt - fit_go: X_cal min={np.min(X_cal):.3f}, max={np.max(X_cal):.3f}, len={len(X_cal)}")
        print(f"PyQt - fit_go: Y_cal min={np.min(Y_cal):.3f}, max={np.max(Y_cal):.3f}, len={len(Y_cal)}")
        print(f"PyQt - fit_go: X_dat min={np.min(X_dat):.3f}, max={np.max(X_dat):.3f}, len={len(X_dat)}")
        print(f"PyQt - fit_go: Y_dat min={np.min(Y_dat):.3f}, max={np.max(Y_dat):.3f}, len={len(Y_dat)}")
    
        # Sort plateaus
        G_cal_setting = self.select_calibration_tab.G_cal_setting
        #plateau_order = sorted(range(len(self.Y_plateaus_cal)), key=lambda k: self.Y_plateaus_cal[k], reverse=(G_cal_setting == 1))
        if G_cal_setting == 1:
            plateau_order = sorted(range(len(self.Y_plateaus_cal)), key=lambda k: self.Y_plateaus_cal[k])[::-1]
        elif G_cal_setting==2:
            plateau_order = sorted(range(len(self.Y_plateaus_cal)), key=lambda k: self.Y_plateaus_cal[k])
        X_plateaus_cal = [self.X_plateaus_cal[i] for i in plateau_order]
        X_plateaus_dat = [self.X_plateaus_dat[i] for i in plateau_order]
        Y_plateaus_cal = [self.Y_plateaus_cal[i] for i in plateau_order]
        Y_plateaus_dat = [self.Y_plateaus_dat[i] for i in plateau_order]
        print(f"Ordered steps: X_plateaus_cal={X_plateaus_cal}, X_plateaus_dat={X_plateaus_dat}, Y_plateaus_cal={Y_plateaus_cal}, Y_plateaus_dat={Y_plateaus_dat}")
        
        # Store plateaus as class attributes for fit_go
        self.X_plateaus_cal = X_plateaus_cal
        self.Y_plateaus_cal = Y_plateaus_cal
        self.X_plateaus_dat = X_plateaus_dat
        self.Y_plateaus_dat = Y_plateaus_dat

        # Compute initial guess
        self.initialguess = []
        for i in range(0, len(Y_plateaus_dat)):
            if i == 0:
                self.initialguess.append(Y_plateaus_dat[i])
            else: 
                self.initialguess.append(Y_plateaus_dat[i] - Y_plateaus_dat[i-1])
        print(f"PyQt - fit_go: initialguess={self.initialguess}")
        print(f"PyQt - fit_go: initialguess stored: {hasattr(self, 'initialguess')}")
    
        # Linear interpolation
        interpolation,linint_ = self.make_func(Y_plateaus_cal)
        self.Y_dat_initialguess_calibrated = interpolation(X_dat, *self.initialguess)
        print(f"PyQt - fit_go: Y_dat_initialguess_calibrated: min={np.min(self.Y_dat_initialguess_calibrated):.3f}, max={np.max(self.Y_dat_initialguess_calibrated):.3f}, len={len(self.Y_dat_initialguess_calibrated)}")
        print(f"PyQt - fit_go: Y_dat_initialguess_calibrated stored: {hasattr(self, 'Y_dat_initialguess_calibrated')}")
        
        self.interpolation = interpolation
        self.linint_=linint_
        

        # Plot calibration overlay
        self.main_window.calibration_tab.figure_calibration_overlay.clear()
        ax = self.main_window.calibration_tab.figure_calibration_overlay.add_subplot(111)
        self.main_window.calibration_tab.redraw_calibration_overlay_init(ax, X_cal, Y_cal, X_dat, self.Y_dat_initialguess_calibrated)
        self.draw_ylabel(Quantity="Calibration", is_log=not self.main_window.select_calibration_tab.scale_cal_data, figure=self.main_window.calibration_tab.figure_calibration_overlay)
        ax.set_xlabel("Depth [µm]")
        self.main_window.calibration_tab.figure_calibration_overlay.tight_layout()
        self.main_window.calibration_tab.canvas_calibration_overlay.draw_idle()
        print("PyQt - Calibration overlay plotted")
    
        # Plot calibration curve
        self.main_window.calibration_tab.figure_calibration_curve.clear()
        ax3 = self.main_window.calibration_tab.figure_calibration_curve.add_subplot(111)
        self.main_window.calibration_tab.redraw_calibration_curve_init(ax3, X_cal, Y_cal, Y_plateaus_dat, Y_plateaus_cal, mode="Calibration")
        k = 0
        for i in range(len(X_plateaus_cal)):
            if (i == 0 and self.fit_includeleft) or (i == len(X_plateaus_cal) - 1 and self.fit_includeright):
                ax3.scatter(np.power(10., Y_plateaus_dat[i]), np.power(10., Y_plateaus_cal[i]), 
                            marker='*', fc='r', s=117, zorder=1)
                print(f"PyQt - Red star (edge, curve): x={np.power(10., Y_plateaus_dat[i]):.3f}, y={np.power(10., Y_plateaus_cal[i]):.3f}")
            else:
                ax3.scatter(np.power(10., Y_plateaus_dat[i]), np.power(10., Y_plateaus_cal[i]), 
                            marker='*', fc='k', s=117, zorder=1)
                print(f"PyQt - Black star (curve): x={np.power(10., Y_plateaus_dat[i]):.3f}, y={np.power(10., Y_plateaus_cal[i]):.3f}")
            if i < len(self.G_fitpoints) and self.G_fitpoints[i] != 0 and i < len(X_plateaus_cal) - 1:
                for _ in range(self.G_fitpoints[i]):
                    k += 1
                    if i + k < len(Y_plateaus_cal):
                        ax3.scatter(np.power(10., Y_plateaus_dat[i + k]), np.power(10., Y_plateaus_cal[i + k]), 
                                    marker='*', fc='darkblue', s=70, zorder=1)
                        print(f"PyQt - Dark blue star (curve, i={i}, k={k}): x={np.power(10., Y_plateaus_dat[i + k]):.3f}, y={np.power(10., Y_plateaus_cal[i]):.3f}")
                        
        self.draw_ylabel(Quantity="Calibration", is_log=not self.main_window.select_calibration_tab.scale_cal_data, figure=self.main_window.calibration_tab.figure_calibration_curve)
        self.draw_xlabel(Quantity="Data",is_log=False)
        self.main_window.calibration_tab.figure_calibration_curve.tight_layout()
        self.main_window.calibration_tab.canvas_calibration_curve.draw_idle()
        print("PyQt - Calibration curve plotted")
    
        self.ui.Fit_go_pushButton.setStyleSheet("background-color: green; color: black")
        self.main_window.calibration_tab.reset_sstart_calib_button_state()
