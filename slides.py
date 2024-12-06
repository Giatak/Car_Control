from PyQt6 import QtCore, QtGui, QtWidgets
import serial
import pygame
import threading
from time import sleep

class JoystickThread(QtCore.QThread):
    joystickMoved = QtCore.pyqtSignal(int, int, int)  # Signal to send throttle, brake, and steering values

    def __init__(self):
        super().__init__()
        pygame.init()

        self.joystick_found = False
        self.joystick = None

    def run(self):
        try:
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
                    
                    # Get the X-axis value of the left joystick (steering)
                    joystick_x_value = self.joystick.get_axis(0)  # Left joystick X-axis for steering
                    # Get the Y-axis value of the right joystick (throttle/brake)
                    joystick_y_value = self.joystick.get_axis(3)  # Right joystick Y-axis for throttle/brake

                    # Map the joystick X-axis value to the steering range
                    steering_value = int(joystick_x_value * 50 + 50)  # Normalize X-axis to [0, 100]

                    # Map the joystick Y-axis value to the throttle and brake ranges
                    if joystick_y_value > 0:  # Joystick pushed up
                        throttle_value = int(joystick_y_value * 100)  # Throttle increases as joystick moves up
                        brake_value = 0  # Brake is 0 when throttle is applied
                    else:  # Joystick pushed down
                        throttle_value = 0  # Throttle is 0 when brake is applied
                        brake_value = int(-joystick_y_value * 100)  # Brake increases as joystick moves down

                    # Emit the signal to update the throttle, brake, and steering values in the main thread
                    self.joystickMoved.emit(throttle_value, brake_value, steering_value)

                sleep(0.03)  # Sleep for a short time to prevent overwhelming the CPU
        except Exception as e:
            print(f"Error in JoystickThread: {e}")

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.serial_port = None
        self.setupUi(self)
        self.setupSerial()  # Initialize serial connection here

        # Initialize joystick thread
        self.joystick_thread = JoystickThread()
        self.joystick_thread.joystickMoved.connect(self.updateControlsFromJoystick)
        self.joystick_thread.start()

        self.is_W_pressed = False
        self.is_S_pressed = False
        self.start_value = 10
        self.max_value = 100
        self.throttleSlider.setValue(0)  # Start throttle slider at 0
        self.brakeSlider.setValue(0)  # Start brake slider at 0
        self.steeringlSlider.setValue(50)  # Start steering at neutral position

    def setupSerial(self):
        """Sets up the serial connection to the Arduino."""
        try:
            self.serial_port = serial.Serial('COM3', 9600, timeout=1)  # Adjust the port if necessary
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
        self.throttleSlider = QtWidgets.QSlider(parent=self.centralwidget)
        self.throttleSlider.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.throttleSlider.setRange(0, 100)
        slider_layout.addWidget(self.throttleSlider)  # Add throttle slider to the slider layout

        # Create a vertical slider for brake
        self.brakeSlider = QtWidgets.QSlider(parent=self.centralwidget)
        self.brakeSlider.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.brakeSlider.setRange(0, 100)
        slider_layout.addWidget(self.brakeSlider)  # Add brake slider to the slider layout

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
        self.pushButton.clicked.connect(self.resetControls)
        self.steeringlSlider.valueChanged.connect(self.DataUpdate)
        self.throttleSlider.valueChanged.connect(self.DataUpdate)
        self.brakeSlider.valueChanged.connect(self.DataUpdate)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "H-000, T-000, B-000"))
        self.label.adjustSize()
        self.pushButton.setText(_translate("MainWindow", "RESET THROTTLE"))
        self.pushButton.setShortcut(_translate("MainWindow", "Space"))

    def resetControls(self):
        self.throttleSlider.setValue(0)
        self.brakeSlider.setValue(0)
        self.steeringlSlider.setValue(50)
        self.DataUpdate()

    def DataUpdate(self):
        s_value = self.steeringlSlider.value()
        t_value = self.throttleSlider.value()
        b_value = self.brakeSlider.value()
        
        if self.serial_port and self.serial_port.is_open:
            message = f"S-{s_value:03}, T-{t_value:03}, B-{b_value:03}\n"
            self.serial_port.write(message.encode())
            print(f"Sent to Arduino: {message.strip()}")
        self.label.setText(f"H-{s_value:03}, T-{t_value:03}, B-{b_value:03}")
        self.label.adjustSize()
        print(f"H-{s_value:03}, T-{t_value:03}, B-{b_value:03}")

    def closeEvent(self, event):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Serial port closed.")
        event.accept()

    def updateControlsFromJoystick(self, throttle_value, brake_value, steering_value):
        """Update the throttle, brake, and steering sliders based on joystick input."""
        self.throttleSlider.setValue(throttle_value)
        self.brakeSlider.setValue(brake_value)
        self.steeringlSlider.setValue(steering_value)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec())
