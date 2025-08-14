from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import sys

def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('PyQt5 Test')
    layout = QVBoxLayout()
    label = QLabel('PyQt5 is installed and working!')
    layout.addWidget(label)
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
