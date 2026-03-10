#!/usr/bin/env python3

import math
import psutil

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32, Bool


class RobotMonitor(Node):

    def __init__(self):
        super().__init__('robot_monitor')

        self.battery_percent = None
        self.robot_speed = 0.0

        self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            10
        )

        self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.battery_pub     = self.create_publisher(Float32, '/robot/battery_percent', 10)
        self.speed_pub       = self.create_publisher(Float32, '/robot/speed', 10)
        self.cpu_pub         = self.create_publisher(Float32, '/robot/cpu_usage', 10)
        self.low_battery_pub = self.create_publisher(Bool,   '/robot/battery_low', 10)

        self.create_timer(1.0, self.publish_status)
        self.get_logger().info('Robot monitor started')

    def battery_callback(self, msg):
        self.battery_percent = msg.percentage

    def odom_callback(self, msg):
        vx = msg.twist.twist.linear.x
        vy = msg.twist.twist.linear.y
        self.robot_speed = math.sqrt(vx ** 2 + vy ** 2)

    def publish_status(self):
        # Battery percentage
        if self.battery_percent is not None:
            msg = Float32()
            msg.data = float(self.battery_percent)
            self.battery_pub.publish(msg)

        # Speed
        speed = Float32()
        speed.data = float(self.robot_speed)
        self.speed_pub.publish(speed)

        # CPU usage
        cpu = Float32()
        cpu.data = float(psutil.cpu_percent())
        self.cpu_pub.publish(cpu)

        # Low battery flag
        low = Bool()
        low.data = (self.battery_percent is not None) and (self.battery_percent < 0.25)
        self.low_battery_pub.publish(low)


def main():
    rclpy.init()
    node = RobotMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
