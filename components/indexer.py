from magicbot import feedback, will_reset_to
import wpilib


class Indexer:
    indexer_motors: list
    indexer_switches: list
    ready_piston: wpilib.DigitalInput

    jogging = will_reset_to(False)

    def on_enable(self) -> None:
        for motor in self.indexer_motors:
            motor.setInverted(True)
        self.indexing = True
        self.speed = 0.2

    def execute(self) -> None:
        if self.jogging:
            for i, motor in enumerate(self.indexer_motors):
                motor.set(self.speed if i != 0 else 0)
            return

        if self.indexing:
            for i, (motor, switch) in enumerate(
                zip(
                    self.indexer_motors,
                    [switch.get() for switch in self.indexer_switches],
                )
            ):

                if switch:
                    if not i:
                        if not self.ready_piston.get():
                            motor.set(self.speed * 2)
                        else:
                            motor.stopMotor()
                    else:
                        motor.set(self.speed)
                else:
                    motor.stopMotor()
        else:
            for motor in self.indexer_motors:
                motor.stopMotor()

    def enable_indexing(self) -> None:
        self.indexing = True

    def disable_indexing(self) -> None:
        self.indexing = False

    def jog(self) -> None:
        """Run the indexer motors only (excluding the injector)."""
        self.jogging = True

    @feedback
    def balls_loaded(self) -> int:
        return sum(not switch.get() for switch in self.indexer_switches)

    @feedback
    def is_ready(self) -> bool:
        return not self.indexer_switches[0].get()
