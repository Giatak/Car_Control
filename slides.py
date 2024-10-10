from PyQt6 import QtCore, QtGui, QtWidgets
import serial
from time import sleep

#H-000, V-020

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.setupUi(self)
        self.setupSerial()
    
    def setupSerial(self):
        # Set up serial port (replace 'COM3' with your Arduino port)
        try:
            self.serial_port = serial.Serial('COM3', 9600, timeout=1)
            sleep(2)  # Wait for the connection to be established
            print("Serial connection established.")
        except serial.SerialException as e:
            print(f"Error: {e}")

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 475)

        # Create the central widget
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Create a vertical layout to organize the main components
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)

        #Create a horixontal layout for the label status
        status_layout = QtWidgets.QHBoxLayout()

        # Create a label to display all the control's data
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(36)
        self.label.setFont(font)
        self.label.setObjectName("label")
        status_layout.addWidget(self.label)  # Add label to the main layout

        # Create a horizontal layout to group the sliders
        slider_layout = QtWidgets.QHBoxLayout()

        # Create a horizontal slider
        self.horizontalSlider = QtWidgets.QSlider(parent=self.centralwidget)
        self.horizontalSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSlider.setRange(0, 100)
        slider_layout.addWidget(self.horizontalSlider)  # Add horizontal slider to the slider layout

        # Create a vertical slider
        self.verticalSlider = QtWidgets.QSlider(parent=self.centralwidget)
        self.verticalSlider.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.verticalSlider.setRange(0, 100)
        slider_layout.addWidget(self.verticalSlider)  # Add vertical slider to the slider layout

        # Add the slider layout to the main layout
        main_layout.addLayout(slider_layout)

        # Create a reset button
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        main_layout.addWidget(self.pushButton)  # Add button to the main layout

        # Set the central widget for the main window
        MainWindow.setCentralWidget(self.centralwidget)

        # Create menu bar
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")

        # Create File and Edit menus
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(parent=self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        MainWindow.setMenuBar(self.menubar)

        # Create actions for menu items
        self.actionNew = QtGui.QAction(parent=MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionSave = QtGui.QAction(parent=MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionCopy = QtGui.QAction(parent=MainWindow)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtGui.QAction(parent=MainWindow)
        self.actionPaste.setObjectName("actionPaste")

        # Add actions to menus
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionSave)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)

        # Add menus to the menu bar
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        # Set up translations and shortcuts
        self.retranslateUi(MainWindow)

        # Connect signals for menu actions
        self.actionNew.triggered.connect(lambda: self.clicked("New was clicked"))
        self.actionSave.triggered.connect(lambda: self.clicked("Save was clicked"))
        self.actionCopy.triggered.connect(lambda: self.clicked("Copy was clicked"))
        self.actionPaste.triggered.connect(lambda: self.clicked("Paste was clicked"))

        # Connect button click and slider value changes
        self.pushButton.clicked.connect(self.resetTHROTTLE)
        self.horizontalSlider.valueChanged.connect(self.DataUpdate)
        self.verticalSlider.valueChanged.connect(self.DataUpdate)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "H-000, V-000"))
        self.label.adjustSize()
        self.pushButton.setText(_translate("MainWindow", "RESET THROTTLE"))
        self.pushButton.setShortcut(_translate("MainWindow", "Space"))

        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))

        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionNew.setStatusTip(_translate("MainWindow", "Create a new file"))
        self.actionNew.setShortcut(_translate("MainWindow", "Ctrl+N"))

        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setStatusTip(_translate("MainWindow", "Save a file"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))

        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionCopy.setStatusTip(_translate("MainWindow", "Copy text"))
        self.actionCopy.setShortcut(_translate("MainWindow", "Ctrl+C"))

        self.actionPaste.setText(_translate("MainWindow", "Paste"))
        self.actionPaste.setStatusTip(_translate("MainWindow", "Paste text"))
        self.actionPaste.setShortcut(_translate("MainWindow", "Ctrl+V"))

    def clicked(self, text):
        self.label.setText(text)
        self.label.adjustSize()
        print(str(text))

    def resetTHROTTLE(self):
        self.verticalSlider.setValue(0)
        self.DataUpdate()

    def DataUpdate(self):
        h_value = self.horizontalSlider.value()
        v_value = self.verticalSlider.value()
        if self.serial_port and self.serial_port.is_open:
            message = "H-" + f"{h_value:03}" + ", V-" + f"{v_value:03}\n"
            self.serial_port.write(message.encode())
            print(f"Sent to Arduino: {message.strip()}")
        self.label.setText("H-" + f"{h_value:03}" + ", V-" + f"{v_value:03}\n")
        self.label.adjustSize()
        print("H-" + f"{h_value:03}" + ", V-" + f"{v_value:03}")

    def closeEvent(self, event):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Serial port closed.")
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_1:
            self.verticalSlider.setValue(0)
        elif event.key() == QtCore.Qt.Key.Key_2:
            self.verticalSlider.setValue(10)
        elif event.key() == QtCore.Qt.Key.Key_3:
            self.verticalSlider.setValue(20)
        elif event.key() == QtCore.Qt.Key.Key_4:
            self.verticalSlider.setValue(30)
        elif event.key() == QtCore.Qt.Key.Key_5:
            self.verticalSlider.setValue(40)
        elif event.key() == QtCore.Qt.Key.Key_6:
            self.verticalSlider.setValue(50)
        elif event.key() == QtCore.Qt.Key.Key_7:
            self.verticalSlider.setValue(60)
        elif event.key() == QtCore.Qt.Key.Key_8:
            self.verticalSlider.setValue(70)
        elif event.key() == QtCore.Qt.Key.Key_9:
            self.verticalSlider.setValue(80)
        elif event.key() == QtCore.Qt.Key.Key_0:
            self.verticalSlider.setValue(100)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec())