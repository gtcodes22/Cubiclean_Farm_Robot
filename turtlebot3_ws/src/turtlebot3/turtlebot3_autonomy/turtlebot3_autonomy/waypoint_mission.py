#!/usr/bin/env python3

import os
import yaml
import time
import threading

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
from ament_index_python.packages import get_package_share_directory


class WaypointMission(Node):

    def __init__(self):
        super().__init__('waypoint_mission')

        self.declare_parameter(
            'waypoints_file',
            os.path.join(
                get_package_share_directory('turtlebot3_autonomy'),
                'config',
                'waypoints.yaml'
            )
        )

        self.navigator = BasicNavigator()
        self.waypoints = self.load_waypoints()
        self.get_logger().info(f"Loaded {len(self.waypoints)} waypoints")

        self._mission_thread = threading.Thread(
            target=self.run_mission, daemon=True
        )
        self._mission_thread.start()

    def load_waypoints(self):
        waypoints_file = self.get_parameter('waypoints_file').value
        self.get_logger().info(f"Loading waypoints from: {waypoints_file}")

        with open(waypoints_file) as f:
            data = yaml.safe_load(f)

        waypoints = []
        for name, wp in data['waypoints'].items():
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.header.stamp = self.get_clock().now().to_msg()

            pose.pose.position.x = float(wp['pose'][0])
            pose.pose.position.y = float(wp['pose'][1])
            pose.pose.position.z = float(wp['pose'][2])

            pose.pose.orientation.w = float(wp['orientation'][0])
            pose.pose.orientation.x = float(wp['orientation'][1])
            pose.pose.orientation.y = float(wp['orientation'][2])
            pose.pose.orientation.z = float(wp['orientation'][3])

            waypoints.append(pose)
            self.get_logger().info(
                f"  Loaded {name}: ({pose.pose.position.x:.2f}, {pose.pose.position.y:.2f})"
            )

        return waypoints

    def set_initial_pose(self):
        self.get_logger().info('Publishing initial pose to /initialpose...')

        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.pose.pose.position.x = 0.0
        msg.pose.pose.position.y = 0.0
        msg.pose.pose.position.z = 0.0
        msg.pose.pose.orientation.x = 0.0
        msg.pose.pose.orientation.y = 0.0
        msg.pose.pose.orientation.z = 0.0
        msg.pose.pose.orientation.w = 1.0
        msg.pose.covariance[0]  = 0.25
        msg.pose.covariance[7]  = 0.25
        msg.pose.covariance[35] = 0.06853891945200942

        pub = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)

        for i in range(5):
            msg.header.stamp = self.get_clock().now().to_msg()
            pub.publish(msg)
            self.get_logger().info(f'  Initial pose publish {i + 1}/5')
            time.sleep(0.5)

        self.get_logger().info('Initial pose sent — waiting for AMCL to localise...')
        time.sleep(2.0)

    def data_logger(self, i):
        self.get_logger().info(f"Logging data at waypoint {i}")

    def run_mission(self):
        self.set_initial_pose()
        self.navigator.waitUntilNav2Active()
        self.get_logger().info("Nav2 is active — starting mission")

        for i, waypoint in enumerate(self.waypoints):
            waypoint.header.stamp = self.get_clock().now().to_msg()
            self.get_logger().info(f"Navigating to waypoint {i}")
            self.navigator.goToPose(waypoint)

            while not self.navigator.isTaskComplete():
                time.sleep(0.5)

            result = self.navigator.getResult()
            self.get_logger().info(f"Waypoint {i} result: {result}")
            self.data_logger(i)
            time.sleep(15)

        self.get_logger().info("Mission complete")


def main():
    rclpy.init()
    node = WaypointMission()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
