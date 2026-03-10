#!/usr/bin/env python3

from sensor_msgs.msg import BatteryState

LOW_BATTERY_THRESHOLD = 0.25


class BatteryMonitor:
    """
    Utility class for monitoring battery state.
    Subscribes to /battery_state and exposes the current percentage
    and a low-battery check method.
    """

    def __init__(self, node):
        self.node = node
        self.percent = None

        node.create_subscription(
            BatteryState,
            '/battery_state',
            self._callback,
            10
        )

    def _callback(self, msg):
        self.percent = msg.percentage

    def battery_low(self):
        if self.percent is None:
            return False
        return self.percent < LOW_BATTERY_THRESHOLD

    def get_percent(self):
        return self.percent
