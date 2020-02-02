#!/usr/bin/env python3

# Copyright (c) 2017-2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.

import ctre
import magicbot
import rev.color
import wpilib

from components.chassis import Chassis
from components.hang import Hang
from components.indexer import Indexer
from components.shooter import Shooter
from components.spinner import Spinner
from components.turret import Turret
from components.vision import Vision
from controllers.shooter import ShooterController
from controllers.spinner import SpinnerController
from utilities.scale_value import scale_value


class MyRobot(magicbot.MagicRobot):
    # List controllers (which require components) here.
    shooter_controller: ShooterController
    spinner_controller: SpinnerController

    # List components (which represent physical subsystems) here.
    chassis: Chassis
    hang: Hang
    indexer: Indexer
    shooter: Shooter
    spinner: Spinner
    turret: Turret

    def createObjects(self):
        """Robot initialization function"""
        self.chassis_left_front = rev.CANSparkMax(5, rev.MotorType.kBrushless)
        self.chassis_left_rear = rev.CANSparkMax(4, rev.MotorType.kBrushless)
        self.chassis_right_front = rev.CANSparkMax(7, rev.MotorType.kBrushless)
        self.chassis_right_rear = rev.CANSparkMax(6, rev.MotorType.kBrushless)

        self.hang_winch_motor_master = ctre.WPI_TalonSRX(21)
        self.hang_winch_motor_slave = ctre.WPI_TalonSRX(22)
        self.hang_kracken_hook_latch = wpilib.DoubleSolenoid(4, 5)

        self.indexer_motors = [ctre.WPI_TalonSRX(3), wpilib.Spark(2), wpilib.Spark(1)]
        # Motors and switches created from injector [0] to intake [4]
        # Or in this case from injector[0] to half-indexer [2]
        self.indexer_switches = [
            wpilib.DigitalInput(9),
            wpilib.DigitalInput(8),
            wpilib.DigitalInput(7),
        ]
        self.ready_piston = wpilib.DigitalInput(4)
        self.injector_slave_motor = ctre.WPI_TalonSRX(43)
        self.injector_slave_motor.follow(self.indexer_motors[0])
        self.injector_slave_motor.setInverted(False)

        self.led = wpilib._wpilib.AddressableLED(0)
        self.loading_piston = wpilib.Solenoid(0)
        self.shooter_centre_motor = rev.CANSparkMax(3, rev.MotorType.kBrushless)
        self.shooter_outer_motor = rev.CANSparkMax(2, rev.MotorType.kBrushless)

        self.colour_sensor = rev.color.ColorSensorV3(wpilib.I2C.Port.kOnboard)

        self.spinner_motor = wpilib.Spark(2)
        self.spinner_solenoid = wpilib.DoubleSolenoid(2, 3)

        self.turret_centre_index = wpilib.DigitalInput(0)
        self.turret_motor = ctre.WPI_TalonSRX(10)

        self.vision = Vision()

        # operator interface
        self.driver_joystick = wpilib.Joystick(0)

    def teleopInit(self):
        """Executed at the start of teleop mode"""

    def teleopPeriodic(self):
        """Executed every cycle"""

        self.handle_spinner_inputs(self.driver_joystick)
        self.handle_chassis_inputs(self.driver_joystick)

        pov = self.driver_joystick.getPOV(0)
        about_five_degrees = 0.087  # radians
        if pov != -1:
            if pov < 180:
                self.turret.slew(about_five_degrees)
            else:
                self.turret.slew(-about_five_degrees)

        self.indexer.speed = scale_value(
            self.driver_joystick.getThrottle(), 1, -1, 0, 0.5
        )
        if self.driver_joystick.getRawButtonPressed(6):
            if self.indexer.indexing:
                self.indexer.disable_indexing()
            else:
                self.indexer.enable_indexing()

        self.handle_spinner_inputs(self.driver_joystick)
        self.handle_shooter_inputs(self.driver_joystick)
        self.handle_hang_inputs(self.driver_joystick)

    def handle_spinner_inputs(self, joystick):
        if joystick.getRawButtonPressed(7):
            self.spinner_controller.run(test=True, task="position")
            print(f"Spinner Running")
        if joystick.getRawButtonPressed(9):
            self.spinner.piston_up()
            print("Spinner Piston Up")
        if joystick.getRawButtonPressed(10):
            self.spinner.piston_down()
            print("Spinner Piston Down")
        if joystick.getRawButtonPressed(8):
            print(f"Detected Colour: {self.spinner_controller.get_current_colour()}")
            print(f"Distance: {self.spinner_controller.get_wheel_dist()}")

    def handle_chassis_inputs(self, joystick):
        scaled_throttle = scale_value(joystick.getThrottle(), 1, -1, 0, 1)
        vx = scale_value(joystick.getY(), 1, -1, -1, 1, 2) * scaled_throttle
        vz = scale_value(joystick.getX(), 1, -1, -1, 1, 2) * scaled_throttle
        self.chassis.drive(vx, vz)

    def handle_shooter_inputs(self, joystick: wpilib.Joystick):
        if joystick.getTriggerPressed():
            self.shooter_controller.driver_input(True)
        if joystick.getTriggerReleased():
            self.shooter_controller.driver_input(False)
        if joystick.getRawButtonPressed(5):
            self.shooter_controller.spin_input()

    def handle_hang_inputs(self, joystick: wpilib.Joystick):
        # if joystick.getRawButtonPressed(3) and joystick.getRawButtonPressed(4):
        #     self.hang.raise_hook()
        # if self.hang.fire_hook and joystick.getRawButtonPressed(4):
        #     self.hang.winch()
        pass


if __name__ == "__main__":
    wpilib.run(MyRobot)
