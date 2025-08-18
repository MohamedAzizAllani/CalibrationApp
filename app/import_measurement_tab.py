import os
import numpy as np
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QSlider
from PyQt5.QtCore import Qt, QSettings
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ImportMeasurementTab:
    """Controller for the 'Import Measurement' tab functionality."""
    def __init__(self, ui, main_window):
        """Initialize the tab with UI elements and data attributes."""
        self.ui = ui
        self.main_window = main_window
        
        # Initialize matplotlib figure and canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        try:
            self.ui.verticalLayout.addWidget(self.canvas)
        except AttributeError as e:
            print(f"Error: {e}. Ensure verticalLayoutWidget has a QVBoxLayout in main_window.ui.")
            raise SystemExit(1)
        
        # Data attributes
        self.X_data = np.array([])  # X-axis data (depth in µm)
        self.Y_data = np.array([])  # Y-axis data (measurement values)
        self.X_data_range = np.array([])  # X-axis data for plotting (flipped or not)
        self.borders_data = [0, 0]  # Current left and right borders
        self.original_borders_data = [0, 0]  # Non-flipped borders
        self.data_is_flipped = False  # Flag for data flip state
        self.measurement_file = ""  # Path to measurement file
        self.G_data_separators = [";", "   ", "\t", ","]  # Possible file delimiters
        self.G_dat_datatype = "SSRM"  # Default data type
        self.denomination = ""  # Custom data denomination for 'Other' type
        
        # Settings for storing last directory
        self.settings = QSettings("MyApp", "Calibration")
        self.last_directory = self.settings.value("last_directory", "", type=str)
        
        # Initialize UI elements
        self.ui.DataDenominationLabel.setVisible(False)
        self.ui.denominationLineEdit.setVisible(False)
        
        # Connect signals to slots
        self.ui.measurementBrowseButton.clicked.connect(self.browse_measurement_file)
        self.ui.applyParametersButton.clicked.connect(self.apply_parameters)
        self.ui.flipDataCheckBox.stateChanged.connect(self.flip_data)
        self.ui.dataTypeComboBox.currentTextChanged.connect(self.update_data_type)
        self.ui.denominationLineEdit.textChanged.connect(self.update_denomination)
        self.ui.leftBorderSlider.valueChanged.connect(self.change_left_border)
        self.ui.rightBorderSlider.valueChanged.connect(self.change_right_border)

    def browse_measurement_file(self):
        """Open file dialog to select a measurement file and import its data."""
        initial_dir = self.last_directory
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window, "Select Measurement File", initial_dir, "Text Files (*.txt)"
        )
        if file_path:
            self.measurement_file = file_path
            self.last_directory = os.path.dirname(file_path)
            self.settings.setValue("last_directory", self.last_directory)
            self.ui.measurementLineEdit.setText(file_path)
            self.import_data(file_path)

    def import_data(self, path_data):
        """Import XY data from a text file with various delimiters."""
        successful_data_import = False
        data = None
        debug = False
        for delim in self.G_data_separators:
            try:
                data = np.loadtxt(path_data, delimiter=delim)
                if len(data.shape) != 2 or data.shape[1] != 2:
                    raise ValueError(f"Expected 2 columns, got shape {data.shape}")
                successful_data_import = True
                break
            except Exception as e:
                if debug:
                    print(f"Failed with delimiter '{delim}': {e}")
                continue
        if successful_data_import:
            try:
                if not np.all(np.isfinite(data)):
                    raise ValueError("Data contains non-numeric or invalid values")
                data[:, 0] = data[:, 0] * 1e6  # Convert X to µm
                X = data[:, 0] - data[:, 0][0]  # Normalize X to start at 0
                Y = data[:, 1]
                if X.size < 2 or Y.size < 2:
                    raise ValueError("Data has too few points")
                borders = [X[0], X[-1]]
                X_range = abs(X[-1])
                self.X_data = X
                self.Y_data = Y
                self.X_data_range = X.copy()
                self.borders_data = borders
                self.original_borders_data = borders.copy()
                self.data_is_flipped = False
                self.ui.dataPathLabel.setText(path_data)
                self.reset_data_window()
                self.redraw_data_preview()
                if debug:
                    print(f"Imported data: shape={data.shape}, X_range={X_range}, borders={borders}")
                QMessageBox.information(self.main_window, "Success", "Measurement data imported successfully!")
                return [True, X, Y, borders, X_range]
            except Exception as e:
                if debug:
                    print(f"Processing error: {e}")
                QMessageBox.critical(self.main_window, "Error", f"Measurement data can be opened but cannot be read as XY: {str(e)}")
                return [False, None, None, None, None]
        else:
            if debug:
                print(f"Failed to read file: {path_data}")
            QMessageBox.critical(self.main_window, "Error", "Measurement data cannot be read")
            return [False, None, None, None, None]

    def update_slider_label_position(self, slider, label, value):
        """Update the position of a slider's value label to follow the handle."""
        min_val = slider.minimum()
        max_val = slider.maximum()
        slider_width = slider.width()
        handle_width = 10
        if max_val > min_val:
            fraction = (value - min_val) / (max_val - min_val)
            x_offset = int(fraction * (slider_width - handle_width)) + slider.x()
            label.setGeometry(x_offset - 30, label.y(), 60, 20)

    def change_left_border(self, value):
        """Update left border based on slider value and ensure valid range."""
        if self.X_data.size > 0:
            min_val = min(self.X_data)
            max_val = max(self.X_data)
            self.borders_data[0] = max(min_val, min(value / 1000.0, max_val))
            if not self.data_is_flipped:
                self.original_borders_data[0] = self.borders_data[0]
            self.ui.rightMinLabel.setText(f"{self.borders_data[0]:.3f} µm")
            self.ui.rightBorderSlider.setMinimum(int(self.borders_data[0] * 1000))
            if self.borders_data[1] < self.borders_data[0]:
                self.borders_data[1] = self.borders_data[0]
                if not self.data_is_flipped:
                    self.original_borders_data[1] = self.borders_data[1]
                self.ui.rightBorderSlider.setValue(int(self.borders_data[1] * 1000))
                self.ui.rightSliderValueLabel.setText(f"{self.borders_data[1]:.3f}")
            self.ui.leftSliderValueLabel.setText(f"{self.borders_data[0]:.3f}")
            self.update_slider_label_position(self.ui.leftBorderSlider, self.ui.leftSliderValueLabel, value)
            self.update_slider_label_position(self.ui.rightBorderSlider, self.ui.rightSliderValueLabel, int(self.borders_data[1] * 1000))
            self.ui.applyParametersButton.setEnabled(True)

    def change_right_border(self, value):
        """Update right border based on slider value and ensure valid range."""
        if self.X_data.size > 0:
            min_val = min(self.X_data)
            max_val = max(self.X_data)
            self.borders_data[1] = max(min_val, min(value / 1000.0, max_val))
            if not self.data_is_flipped:
                self.original_borders_data[1] = self.borders_data[1]
            self.ui.leftMaxLabel.setText(f"{self.borders_data[1]:.3f} µm")
            self.ui.leftBorderSlider.setMaximum(int(self.borders_data[1] * 1000))
            if self.borders_data[0] > self.borders_data[1]:
                self.borders_data[0] = self.borders_data[1]
                if not self.data_is_flipped:
                    self.original_borders_data[0] = self.borders_data[0]
                self.ui.leftBorderSlider.setValue(int(self.borders_data[0] * 1000))
                self.ui.leftSliderValueLabel.setText(f"{self.borders_data[0]:.3f}")
            self.ui.rightSliderValueLabel.setText(f"{self.borders_data[1]:.3f}")
            self.update_slider_label_position(self.ui.rightBorderSlider, self.ui.rightSliderValueLabel, value)
            self.update_slider_label_position(self.ui.leftBorderSlider, self.ui.leftSliderValueLabel, int(self.borders_data[0] * 1000))
            self.ui.applyParametersButton.setEnabled(True)

    def reset_data_window(self):
        """Reset sliders, labels, and UI elements to initial data state."""
        if self.X_data.size > 0:
            min_val = min(self.X_data) * 1000
            max_val = max(self.X_data) * 1000
            self.ui.leftBorderSlider.setMinimum(int(min_val))
            self.ui.leftBorderSlider.setMaximum(int(max_val))
            self.ui.leftBorderSlider.setSingleStep(1000)  # 1 µm steps
            self.ui.leftBorderSlider.setPageStep(1000)   # Match singleStep
            self.ui.leftBorderSlider.setValue(int(self.borders_data[0] * 1000))
            self.ui.leftBorderSlider.setTickPosition(QSlider.TicksBothSides)
            self.ui.leftBorderSlider.setTickInterval(int((max_val - min_val) / 10))
            self.ui.rightBorderSlider.setMinimum(int(min_val))
            self.ui.rightBorderSlider.setMaximum(int(max_val))
            self.ui.rightBorderSlider.setSingleStep(1000)  # 1 µm steps
            self.ui.rightBorderSlider.setPageStep(1000)   # Match singleStep
            self.ui.rightBorderSlider.setValue(int(self.borders_data[1] * 1000))
            self.ui.rightBorderSlider.setTickPosition(QSlider.TicksBothSides)
            self.ui.rightBorderSlider.setTickInterval(int((max_val - min_val) / 10))
            
            # Apply stylesheets
            self.ui.leftBorderSlider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #999999;
                    height: 8px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B0C4DE, stop:1 #B0C4DE);
                    margin: 2px 0;
                }
                QSlider::handle:horizontal {
                    background: #4682B4;
                    border: 1px solid #2F4F4F;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 3px;
                }
            """)
            self.ui.rightBorderSlider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #999999;
                    height: 8px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFB6C1, stop:1 #FFB6C1);
                    margin: 2px 0;
                }
                QSlider::handle:horizontal {
                    background: #DC143C;
                    border: 1px solid #2F4F4F;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 3px;
                }
            """)
            
            self.ui.leftMinLabel.setText(f"{min(self.X_data):.3f} µm")
            self.ui.leftMaxLabel.setText(f"{max(self.X_data):.3f} µm")
            self.ui.rightMinLabel.setText(f"{self.borders_data[0]:.3f} µm")
            self.ui.rightMaxLabel.setText(f"{max(self.X_data):.3f} µm")
            self.ui.leftSliderValueLabel.setText(f"{self.borders_data[0]:.3f}")
            self.ui.rightSliderValueLabel.setText(f"{self.borders_data[1]:.3f}")
            self.update_slider_label_position(self.ui.leftBorderSlider, self.ui.leftSliderValueLabel, int(self.borders_data[0] * 1000))
            self.update_slider_label_position(self.ui.rightBorderSlider, self.ui.rightSliderValueLabel, int(self.borders_data[1] * 1000))

    def flip_dataset(self):
        """Flip the dataset and update borders, sliders, and labels."""
        if self.X_data.size > 0:
            max_x = max(self.X_data)
            min_x = min(self.X_data)
            if self.data_is_flipped:
                self.X_data_range = self.X_data[::-1]
                left_border = max_x - (self.original_borders_data[0] - min_x)
                right_border = max_x - (self.original_borders_data[1] - min_x)
                self.borders_data = [min(left_border, right_border), max(left_border, right_border)]
            else:
                self.X_data_range = self.X_data.copy()
                self.borders_data = self.original_borders_data.copy()
            min_val = min(self.X_data_range) * 1000
            max_val = max(self.X_data_range) * 1000
            self.ui.leftBorderSlider.setMinimum(int(min_val))
            self.ui.leftBorderSlider.setMaximum(int(max_val))
            self.ui.leftBorderSlider.setSingleStep(1000)  # 1 µm steps
            self.ui.leftBorderSlider.setPageStep(1000)   # Match singleStep
            self.ui.leftBorderSlider.setValue(int(self.borders_data[0] * 1000))
            self.ui.leftBorderSlider.setTickPosition(QSlider.TicksBothSides)
            self.ui.leftBorderSlider.setTickInterval(int((max_val - min_val) / 10))
            self.ui.rightBorderSlider.setMinimum(int(min_val))
            self.ui.rightBorderSlider.setMaximum(int(max_val))
            self.ui.rightBorderSlider.setSingleStep(1000)  # 1 µm steps
            self.ui.rightBorderSlider.setPageStep(1000)   # Match singleStep
            self.ui.rightBorderSlider.setValue(int(self.borders_data[1] * 1000))
            self.ui.rightBorderSlider.setTickPosition(QSlider.TicksBothSides)
            self.ui.rightBorderSlider.setTickInterval(int((max_val - min_val) / 10))
            self.ui.leftBorderSlider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #999999;
                    height: 8px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B0C4DE, stop:1 #B0C4DE);
                    margin: 2px 0;
                }
                QSlider::handle:horizontal {
                    background: #4682B4;
                    border: 1px solid #2F4F4F;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 3px;
                }
            """)
            self.ui.rightBorderSlider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #999999;
                    height: 8px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFB6C1, stop:1 #FFB6C1);
                    margin: 2px 0;
                }
                QSlider::handle:horizontal {
                    background: #DC143C;
                    border: 1px solid #2F4F4F;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 3px;
                }
            """)
            self.ui.leftMinLabel.setText(f"{min(self.X_data_range):.3f} µm")
            self.ui.leftMaxLabel.setText(f"{self.borders_data[1]:.3f} µm")
            self.ui.rightMinLabel.setText(f"{self.borders_data[0]:.3f} µm")
            self.ui.rightMaxLabel.setText(f"{max(self.X_data_range):.3f} µm")
            self.ui.leftSliderValueLabel.setText(f"{self.borders_data[0]:.3f}")
            self.ui.rightSliderValueLabel.setText(f"{self.borders_data[1]:.3f}")
            self.update_slider_label_position(self.ui.leftBorderSlider, self.ui.leftSliderValueLabel, int(self.borders_data[0] * 1000))
            self.update_slider_label_position(self.ui.rightBorderSlider, self.ui.rightSliderValueLabel, int(self.borders_data[1] * 1000))

    def update_data_type(self, data_type):
        """Update data type and show/hide denomination input."""
        self.G_dat_datatype = data_type
        is_other = data_type == "Other"
        self.ui.DataDenominationLabel.setVisible(is_other)
        self.ui.denominationLineEdit.setVisible(is_other)
        self.ui.applyParametersButton.setEnabled(True)

    def update_denomination(self, text):
        """Update denomination for 'Other' data type."""
        self.denomination = text
        self.ui.applyParametersButton.setEnabled(True)

    def apply_parameters(self):
        """Apply current parameters and redraw the plot."""
        self.redraw_data_preview()
        QMessageBox.information(self.main_window, "Success", "Parameters applied!")
        self.ui.applyParametersButton.setEnabled(False)

    def redraw_data_preview(self):
        """Redraw the data preview plot with current borders and flip state."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if self.X_data.size > 1:
            min_val = min(self.X_data)
            max_val = max(self.X_data)
            left_border = max(min_val, min(self.borders_data[0], max_val))
            right_border = max(min_val, min(self.borders_data[1], max_val))
            if left_border > right_border:
                left_border, right_border = right_border, left_border
            mask = (self.X_data_range >= left_border) & (self.X_data_range <= right_border)
            if mask.any():
                indices = np.where(mask)[0]
                ax.plot(self.X_data_range[indices], self.Y_data[indices], label='Measurement', color='blue')
                ax.legend()
                y_visible = self.Y_data[indices]
                if y_visible.size > 1:
                    y_min, y_max = min(y_visible), max(y_visible)
                    if y_min == y_max:
                        y_min -= 0.1 * abs(y_min) or 0.1
                        y_max += 0.1 * abs(y_max) or 0.1
                    ax.set_ylim(y_min, y_max)
                else:
                    ax.set_ylim(min(self.Y_data), max(self.Y_data))
            ax.set_xlabel('Depth [µm]')
            ax.set_ylabel('SSRM measured resistance [$\Omega$]' if self.G_dat_datatype == "SSRM" else self.denomination)
            ax.tick_params(axis='both', which='major', labelsize=10)
            ax.tick_params(axis='both', which='minor', labelsize=10)
            ax.grid(True)
        self.canvas.draw()

    def flip_data(self, state):
        """Handle flip checkbox state change and update plot."""
        self.data_is_flipped = state == Qt.Checked
        self.flip_dataset()
        self.redraw_data_preview()
        self.ui.applyParametersButton.setEnabled(True)

    def keyPressEvent(self, event):
        """Handle keyboard input for precise slider adjustments."""
        if self.X_data.size > 0:
            step = 1000  # 1 µm step
            if event.key() == Qt.Key_Left:
                if self.ui.leftBorderSlider.hasFocus():
                    current = self.ui.leftBorderSlider.value()
                    self.ui.leftBorderSlider.setValue(current - step)
                elif self.ui.rightBorderSlider.hasFocus():
                    current = self.ui.rightBorderSlider.value()
                    self.ui.rightBorderSlider.setValue(current - step)
            elif event.key() == Qt.Key_Right:
                if self.ui.leftBorderSlider.hasFocus():
                    current = self.ui.leftBorderSlider.value()
                    self.ui.leftBorderSlider.setValue(current + step)
                elif self.ui.rightBorderSlider.hasFocus():
                    current = self.ui.rightBorderSlider.value()
                    self.ui.rightBorderSlider.setValue(current + step)