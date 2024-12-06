from PyQt6 import QtCore, QtGui, QtWidgets
import serial
from time import sleep
import pygame
import threading

class JoystickThread(QtCore.QThread):
    joystickMoved = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        pygame.init()

        self.joystick_found = False
        self.joystick = None

    def run(self):
        while True:
            # Recheck joystick availability
            joystick_count = pygame.joystick.get_count()
            if joystick_count > 0 and not self.joystick_found:
                self.joystick = pygame.joystick.Joystick(0)  # Use the first joystick
                self.joystick.init()
                self.joystick_found = True
                print(f"Joystick detected: {self.joystick.get_name()}")
            elif joystick_count == 0 and self.joystick_found:
                self.joystick_found = False
                self.joystick = None
                print("Joystick disconnected")

            if self.joystick_found:
                pygame.event.pump()  # Process joystick events
                axis_value = self.joystick.get_axis(0)  # Get the X-axis value (change the axis if needed)

                # Map the joystick axis value to the slider range (0 to 100)
                slider_value = int((axis_value + 1) * 50)  # axis_value ranges from -1 to 1, map to 0 to 100

                # Emit the signal to update the slider value in the main thread
                self.joystickMoved.emit(slider_value)

            sleep(0.03)  # Sleep for a short time to prevent overwhelming the CPU

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.serial_port = None
        self.setupUi(self)
        self.setupSerial()

        # Initialize joystick thread
        self.joystick_thread = JoystickThread()
        self.joystick_thread.joystickMoved.connect(self.updateSteeringSlider)
        self.joystick_thread.start()

        self.is_W_pressed = False
        self.is_S_pressed = False
        self.start_value = 10
        self.max_value = 100
        self.verticalSlider.setValue(0)  # Start slider at 0

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

        # Create a horizontal layout for the label status
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

        # Create a horizontal slider (steering)
        self.steeringlSlider = QtWidgets.QSlider(parent=self.centralwidget)
        self.steeringlSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.steeringlSlider.setRange(0, 100)
        slider_layout.addWidget(self.steeringlSlider)  # Add horizontal slider to the slider layout

        # Create a vertical slider for throttle
        self.breakSlider = QtWidgets.QSlider(parent=self.centralwidget)
        self.breakSlider.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.breakSlider.setRange(0, 100)
        slider_layout.addWidget(self.breakSlider)  # Add vertical slider to the slider layout

        # Create a vertical slider for throttle
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

        # Set up translations and shortcuts
        self.retranslateUi(MainWindow)

        # Connect button click and slider value changes
        self.pushButton.clicked.connect(self.resetTHROTTLE)
        self.steeringlSlider.valueChanged.connect(self.DataUpdate)
        self.verticalSlider.valueChanged.connect(self.DataUpdate)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "H-000, V-000"))
        self.label.adjustSize()
        self.pushButton.setText(_translate("MainWindow", "RESET THROTTLE"))
        self.pushButton.setShortcut(_translate("MainWindow", "Space"))

    def resetTHROTTLE(self):
        self.verticalSlider.setValue(0)
        self.DataUpdate()

    def DataUpdate(self):
        h_value = self.steeringlSlider.value()
        v_value = self.verticalSlider.value()
        if self.serial_port and self.serial_port.is_open:
            message = "S-" + f"{h_value:03}" + ", V-" + f"{v_value:03}\n"
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

    def updateSteeringSlider(self, slider_value):
        """Update the horizontal slider based on joystick X-axis movement."""
        self.steeringlSlider.setValue(slider_value)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_W and not self.is_W_pressed:
            self.is_W_pressed = True
            self.verticalSlider.setValue(min(self.verticalSlider.value() + 5, 100))
            self.DataUpdate()
        elif event.key() == QtCore.Qt.Key.Key_S and not self.is_S_pressed:
            self.is_S_pressed = True
            self.verticalSlider.setValue(max(self.verticalSlider.value() - 5, 0))
            self.DataUpdate()

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_W:
            self.is_W_pressed = False  # Stop incrementing when the key is released
        elif event.key() == QtCore.Qt.Key.Key_S:
            self.is_S_pressed = False  # Stop decrementing when the key is released

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec())
