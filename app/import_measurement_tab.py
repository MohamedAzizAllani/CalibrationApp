import os
import numpy as np
from typing import List, Tuple, Optional

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QSlider
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# --------------------------- Constants & Styles --------------------------- #

APP_ORG = "MyApp"
APP_NAME = "Calibration"

DATA_SEPARATORS_DEFAULT: List[str] = [";", "   ", "\t", ","]
DEFAULT_DATA_TYPE = "SSRM"
SLIDER_STEP_UM = 1000  # 1 µm in slider units (slider values are in 1e-3 µm)

# Styles for sliders (kept identical; centralized for consistency)
LEFT_SLIDER_STYLESHEET = """
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
"""

RIGHT_SLIDER_STYLESHEET = """
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
"""


class ImportMeasurementTab:
    """Controller for the 'Import Measurement' tab functionality."""

    # --------------------------- Init & Wiring --------------------------- #

    def __init__(self, ui, main_window):
        """Initialize the tab with UI elements and data attributes."""
        self.ui = ui
        self.main_window = main_window

        # Matplotlib figure/canvas
        self.figure: Figure = Figure()
        self.canvas: FigureCanvas = FigureCanvas(self.figure)

        try:
            self.ui.verticalLayout.addWidget(self.canvas)
        except AttributeError as e:
            print(f"Error: {e}. Ensure verticalLayoutWidget has a QVBoxLayout in main_window.ui.")
            raise SystemExit(1)

        # Data attributes
        self.X_data: np.ndarray = np.array([])            # original X (µm, normalized)
        self.Y_data: np.ndarray = np.array([])            # original Y
        self.X_data_range: np.ndarray = np.array([])      # X used for plotting (flipped or not)
        self.borders_data: List[float] = [0.0, 0.0]       # current L/R borders (µm)
        self.original_borders_data: List[float] = [0.0, 0.0]  # borders for non-flipped view
        self.data_is_flipped: bool = False
        self.measurement_file: str = ""
        self.G_data_separators: List[str] = DATA_SEPARATORS_DEFAULT.copy()
        self.G_dat_datatype: str = DEFAULT_DATA_TYPE
        self.denomination: str = ""
        self.G_dat_denomination: Optional[str] = None
        self.path_data: Optional[str] = None

        # Settings
        self.settings = QSettings(APP_ORG, APP_NAME)
        self.last_directory: str = self.settings.value("last_directory", "", type=str)

        # UI init
        self._init_ui_visibility()

        # Signal wiring
        self._connect_signals()

    # --------------------------- UI Helpers --------------------------- #

    def _init_ui_visibility(self) -> None:
        """Initial UI visibility state."""
        self.ui.DataDenominationLabel.setVisible(False)
        self.ui.denominationLineEdit.setVisible(False)

    def _connect_signals(self) -> None:
        """Connect Qt signals to slots."""
        self.ui.measurementBrowseButton.clicked.connect(self.browse_measurement_file)
        self.ui.applyParametersButton.clicked.connect(self.apply_parameters)
        self.ui.flipDataCheckBox.stateChanged.connect(self.flip_data)
        self.ui.dataTypeComboBox.currentTextChanged.connect(self.update_data_type)
        self.ui.denominationLineEdit.textChanged.connect(self.update_denomination)
        self.ui.leftBorderSlider.valueChanged.connect(self.change_left_border)
        self.ui.rightBorderSlider.valueChanged.connect(self.change_right_border)

    # --------------------------- File Import --------------------------- #

    def browse_measurement_file(self) -> None:
        """Open file dialog to select a measurement file and import its data."""
        initial_dir = self.last_directory
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window, "Select Measurement File", initial_dir,
        )
        # original commented filter kept:
        # "Text Files (*.txt)"

        if file_path:
            self.measurement_file = file_path
            self.last_directory = os.path.dirname(file_path)
            self.settings.setValue("last_directory", self.last_directory)
            self.ui.measurementLineEdit.setText(file_path)
            self.ui.flipDataCheckBox.setChecked(False)
            self.import_data(file_path)
            self.main_window.alignment_tab.reset_data_state()

    def import_data(self, path_data: str) -> List[object]:
        """Import XY data from a text file with various delimiters."""
        successful_data_import = False
        data = None
        debug = False

        # Try multiple separators
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

                # Convert & normalize X
                data[:, 0] = data[:, 0] * 1e6  # Convert X to µm
                X = data[:, 0] - data[:, 0][0]
                Y = data[:, 1]

                if X.size < 2 or Y.size < 2:
                    raise ValueError("Data has too few points")

                borders = [float(X[0]), float(X[-1])]
                X_range = abs(float(X[-1]))

                # Persist
                self.X_data = X
                self.Y_data = Y
                self.X_data_range = X.copy()
                self.borders_data = borders
                self.original_borders_data = borders.copy()
                self.data_is_flipped = False
                self.ui.dataPathLabel.setText(path_data)
                self.reset_data_window()
                self.redraw_data_preview()
                self.path_data = path_data

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

    # --------------------------- Slider Utilities --------------------------- #

    def update_slider_label_position(self, slider: QSlider, label, value: int) -> None:
        """Update the position of a slider's value label to follow the handle."""
        min_val = slider.minimum()
        max_val = slider.maximum()
        slider_width = slider.width()
        handle_width = 10

        if max_val > min_val:
            fraction = (value - min_val) / (max_val - min_val)
            x_offset = int(fraction * (slider_width - handle_width)) + slider.x()
            label.setGeometry(x_offset - 30, label.y(), 60, 20)

    # --------------------------- Borders & Flip --------------------------- #

    def change_left_border(self, value: int) -> None:
        """Update left border based on slider value and ensure valid range."""
        if self.X_data.size > 0:
            min_val = float(np.min(self.X_data))
            max_val = float(np.max(self.X_data))

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

            self.main_window.alignment_tab.reset_data_state()
            self.ui.applyParametersButton.setEnabled(True)

    def change_right_border(self, value: int) -> None:
        """Update right border based on slider value and ensure valid range."""
        if self.X_data.size > 0:
            min_val = float(np.min(self.X_data))
            max_val = float(np.max(self.X_data))

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

            self.main_window.alignment_tab.reset_data_state()
            self.ui.applyParametersButton.setEnabled(True)

    def reset_data_window(self) -> None:
        """Reset sliders, labels, and UI elements to initial data state."""
        if self.X_data.size > 0:
            min_val = float(np.min(self.X_data)) * 1000
            max_val = float(np.max(self.X_data)) * 1000

            # Left slider
            self.ui.leftBorderSlider.setMinimum(int(min_val))
            self.ui.leftBorderSlider.setMaximum(int(max_val))
            self.ui.leftBorderSlider.setSingleStep(SLIDER_STEP_UM)
            self.ui.leftBorderSlider.setPageStep(SLIDER_STEP_UM)
            self.ui.leftBorderSlider.setValue(int(self.borders_data[0] * 1000))
            self.ui.leftBorderSlider.setTickPosition(QSlider.TicksBothSides)
            self.ui.leftBorderSlider.setTickInterval(int((max_val - min_val) / 10))

            # Right slider
            self.ui.rightBorderSlider.setMinimum(int(min_val))
            self.ui.rightBorderSlider.setMaximum(int(max_val))
            self.ui.rightBorderSlider.setSingleStep(SLIDER_STEP_UM)
            self.ui.rightBorderSlider.setPageStep(SLIDER_STEP_UM)
            self.ui.rightBorderSlider.setValue(int(self.borders_data[1] * 1000))
            self.ui.rightBorderSlider.setTickPosition(QSlider.TicksBothSides)
            self.ui.rightBorderSlider.setTickInterval(int((max_val - min_val) / 10))

            # Styles
            self.ui.leftBorderSlider.setStyleSheet(LEFT_SLIDER_STYLESHEET)
            self.ui.rightBorderSlider.setStyleSheet(RIGHT_SLIDER_STYLESHEET)

            # Labels
            self.ui.leftMinLabel.setText(f"{np.min(self.X_data):.3f} µm")
            self.ui.leftMaxLabel.setText(f"{np.max(self.X_data):.3f} µm")
            self.ui.rightMinLabel.setText(f"{self.borders_data[0]:.3f} µm")
            self.ui.rightMaxLabel.setText(f"{np.max(self.X_data):.3f} µm")
            self.ui.leftSliderValueLabel.setText(f"{self.borders_data[0]:.3f}")
            self.ui.rightSliderValueLabel.setText(f"{self.borders_data[1]:.3f}")

            self.update_slider_label_position(self.ui.leftBorderSlider, self.ui.leftSliderValueLabel, int(self.borders_data[0] * 1000))
            self.update_slider_label_position(self.ui.rightBorderSlider, self.ui.rightSliderValueLabel, int(self.borders_data[1] * 1000))

    def flip_dataset(self) -> None:
        """Flip the dataset and update borders, sliders, and labels."""
        if self.X_data.size > 0:
            max_x = float(np.max(self.X_data))
            min_x = float(np.min(self.X_data))

            if self.data_is_flipped:
                self.X_data_range = self.X_data[::-1]
                left_border = max_x - (self.original_borders_data[0] - min_x)
                right_border = max_x - (self.original_borders_data[1] - min_x)
                self.borders_data = [min(left_border, right_border), max(left_border, right_border)]
            else:
                self.X_data_range = self.X_data.copy()
                self.borders_data = self.original_borders_data.copy()

            # Update sliders to the (possibly) new range
            min_val = float(np.min(self.X_data_range)) * 1000
            max_val = float(np.max(self.X_data_range)) * 1000

            for slider, value in (
                (self.ui.leftBorderSlider, int(self.borders_data[0] * 1000)),
                (self.ui.rightBorderSlider, int(self.borders_data[1] * 1000)),
            ):
                slider.setMinimum(int(min_val))
                slider.setMaximum(int(max_val))
                slider.setSingleStep(SLIDER_STEP_UM)
                slider.setPageStep(SLIDER_STEP_UM)
                slider.setValue(value)
                slider.setTickPosition(QSlider.TicksBothSides)
                slider.setTickInterval(int((max_val - min_val) / 10))

            # Styles
            self.ui.leftBorderSlider.setStyleSheet(LEFT_SLIDER_STYLESHEET)
            self.ui.rightBorderSlider.setStyleSheet(RIGHT_SLIDER_STYLESHEET)

            # Labels
            self.ui.leftMinLabel.setText(f"{np.min(self.X_data_range):.3f} µm")
            self.ui.leftMaxLabel.setText(f"{self.borders_data[1]:.3f} µm")
            self.ui.rightMinLabel.setText(f"{self.borders_data[0]:.3f} µm")
            self.ui.rightMaxLabel.setText(f"{np.max(self.X_data_range):.3f} µm")
            self.ui.leftSliderValueLabel.setText(f"{self.borders_data[0]:.3f}")
            self.ui.rightSliderValueLabel.setText(f"{self.borders_data[1]:.3f}")

            self.update_slider_label_position(self.ui.leftBorderSlider, self.ui.leftSliderValueLabel, int(self.borders_data[0] * 1000))
            self.update_slider_label_position(self.ui.rightBorderSlider, self.ui.rightSliderValueLabel, int(self.borders_data[1] * 1000))

    # --------------------------- Datatype & Denomination --------------------------- #

    def update_data_type(self, data_type: str) -> None:
        """Update data type and show/hide denomination input."""
        self.G_dat_datatype = data_type
        is_other = data_type == "Other"
        self.ui.DataDenominationLabel.setVisible(is_other)
        self.ui.denominationLineEdit.setVisible(is_other)
        self.ui.applyParametersButton.setEnabled(True)

    def update_denomination(self, text: str) -> None:
        """Update denomination for 'Other' data type."""
        self.denomination = text
        self.G_dat_denomination = self.denomination
        self.ui.applyParametersButton.setEnabled(True)

    # --------------------------- Apply & Redraw --------------------------- #

    def apply_parameters(self) -> None:
        """Apply current parameters and redraw the plot."""
        self.redraw_data_preview()
        self.main_window.alignment_tab.reset_data_state()
        QMessageBox.information(self.main_window, "Success", "Parameters applied!")
        self.ui.applyParametersButton.setEnabled(False)

    def redraw_data_preview(self) -> None:
        """Redraw the data preview plot with current borders and flip state."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if self.X_data.size > 1:
            min_x = float(np.min(self.X_data))
            max_x = float(np.max(self.X_data))

            left_border = max(min_x, min(self.borders_data[0], max_x))
            right_border = max(min_x, min(self.borders_data[1], max_x))
            if left_border > right_border:
                left_border, right_border = right_border, left_border

            mask = (self.X_data_range >= left_border) & (self.X_data_range <= right_border)
            if mask.any():
                idx = np.where(mask)[0]
                ax.plot(self.X_data_range[idx], self.Y_data[idx], label='Measurement', color='blue')
                ax.legend()

                y_visible = self.Y_data[idx]
                if y_visible.size > 1:
                    y_min, y_max = float(np.min(y_visible)), float(np.max(y_visible))
                    if y_min == y_max:
                        y_min -= 0.1 * abs(y_min) or 0.1
                        y_max += 0.1 * abs(y_max) or 0.1
                    ax.set_ylim(y_min, y_max)
                else:
                    ax.set_ylim(float(np.min(self.Y_data)), float(np.max(self.Y_data)))

            ax.set_xlabel('Depth [µm]')
            ax.set_ylabel('SSRM measured resistance [$\\Omega$]' if self.G_dat_datatype == "SSRM" else self.denomination)
            ax.tick_params(axis='both', which='major', labelsize=10)
            ax.tick_params(axis='both', which='minor', labelsize=10)
            ax.grid(True)

        self.canvas.draw()

    # --------------------------- Misc --------------------------- #

    def flip_data(self, state) -> None:
        """Handle flip checkbox state change and update plot."""
        self.data_is_flipped = state == Qt.Checked
        self.flip_dataset()
        self.redraw_data_preview()
        self.main_window.alignment_tab.reset_data_state()
        self.ui.applyParametersButton.setEnabled(True)

    def keyPressEvent(self, event) -> None:
        """Handle keyboard input for precise slider adjustments."""
        if self.X_data.size > 0:
            step = SLIDER_STEP_UM  # 1 µm step
            if event.key() == Qt.Key_Left:
                if self.ui.leftBorderSlider.hasFocus():
                    self.ui.leftBorderSlider.setValue(self.ui.leftBorderSlider.value() - step)
                elif self.ui.rightBorderSlider.hasFocus():
                    self.ui.rightBorderSlider.setValue(self.ui.rightBorderSlider.value() - step)
            elif event.key() == Qt.Key_Right:
                if self.ui.leftBorderSlider.hasFocus():
                    self.ui.leftBorderSlider.setValue(self.ui.leftBorderSlider.value() + step)
                elif self.ui.rightBorderSlider.hasFocus():
                    self.ui.rightBorderSlider.setValue(self.ui.rightBorderSlider.value() + step)
