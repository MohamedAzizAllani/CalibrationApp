import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Add project root to path
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from generated_ui.main_window import Ui_MainWindow
from app.import_measurement_tab import ImportMeasurementTab
from app.select_calibration_tab import SelectCalibrationTab


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
        

if __name__ == "__main__":
    """Entry point for the application."""
    # Set high DPI scaling before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())