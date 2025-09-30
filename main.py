import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Add project root to path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from generated_ui.main_window import Ui_MainWindow
from app.import_measurement_tab import ImportMeasurementTab
from app.select_calibration_tab import SelectCalibrationTab
from app.alignment import AlignmentTab
from app.fitpoints import FitpointsTab
from app.calibration import CalibrationTab

class MainApp(QMainWindow):
    """Main application class coordinating all tabs."""
    def __init__(self):
        """Initialize the main window and tab controllers."""
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Center the window on the screen
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

        # Initialize tab controllers
        self.import_measurement_tab = ImportMeasurementTab(self.ui, self)
        self.select_calibration_tab = SelectCalibrationTab(self.ui, self)
        self.alignment_tab = AlignmentTab(self.ui, self)
        self.fitpoints_tab = FitpointsTab(self.ui, self)
        self.calibration_tab = CalibrationTab(self.ui, self)

        # Connect calibration start button
        try:
            self.ui.calibration_startt_pushButton.clicked.connect(self.calibration_tab.calibration_start)
            print("PyQt - calibration_startt_pushButton connected")
        except AttributeError as e:
            print(f"Error: {e}. Ensure calibration_startt_pushButton exists in UI.")
            raise SystemExit(1)

        # Initialize UI after all tabs are set
        self.select_calibration_tab.update_calibration_sample("pcal")
        

if __name__ == "__main__":
    """Entry point for the application."""
    # Set high DPI scaling before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())