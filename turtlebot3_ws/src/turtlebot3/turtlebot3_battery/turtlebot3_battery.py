import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
import socket
import json


TCP_IP = "192.168.1.100"   # IP of the server
TCP_PORT = 5000


class BatterySender(Node):

    def __init__(self):
        super().__init__('battery_sender')

        self.subscription = self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            10)

        # TCP connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((TCP_IP, TCP_PORT))

    def battery_callback(self, msg):

        data = {
            "voltage": msg.voltage,
            "percentage": msg.percentage,
            "current": msg.current
        }

        message = json.dumps(data)
        self.sock.send(message.encode())

        self.get_logger().info(f"Sent: {message}")


def main(args=None):
    rclpy.init(args=args)

    node = BatterySender()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()