import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from generated_ui.main_window import Ui_MainWindow  # Import the generated UI


#entry point of your application

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect buttons to their respective functions
        self.ui.apply_parameters_Button.clicked.connect(lambda: self.show_message("Button 1 Clicked!"))
        self.ui.pushButton_2.clicked.connect(lambda: self.show_message("Button 2 Clicked!"))
        

    def show_message(self, message):
        # Display a pop-up message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle("Button Clicked")
        msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
