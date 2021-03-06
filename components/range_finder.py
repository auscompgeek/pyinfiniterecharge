import wpilib

from magicbot import feedback


class RangeFinder:
    range_counter: wpilib.Counter

    def __init__(self):
        self.distance = 0

    def setup(self):
        self.range_counter.setSemiPeriodMode(highSemiPeriod=True)
        self.range_counter.setSamplesToAverage(10)

    def _get_distance(self):
        # 10 usec is 1cm, return as metres
        return self.range_counter.getPeriod() * 1000000 / 1000

    def execute(self):
        # get the distance and gate it at max range
        d = self._get_distance()
        if d > 40.0:  # Max range is around 40m
            d = 40.0
        self.distance = d

    @feedback
    def get_distance(self):
        return self.distance
