import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import yaml

def main():
    rclpy.init()
    navigator = BasicNavigator()

    # Load waypoints from YAML
    with open('waypoints.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    goal_poses = []
    for pt in data['waypoints']:
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = navigator.get_clock().now().to_msg()
        pose.pose.position.x = float(pt['x'])
        pose.pose.position.y = float(pt['y'])
        pose.pose.orientation.z = float(pt.get('z', 0.0))
        pose.pose.orientation.w = float(pt.get('w', 1.0))
        goal_poses.append(pose)

    # Wait for Nav2 to be active
    navigator.waitUntilNav2Active()

    # Send the waypoints
    print(f"Sending {len(goal_poses)} waypoints...")
    navigator.followWaypoints(goal_poses)

    # Monitor progress
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback:
            print(f'Executing waypoint: {feedback.current_waypoint}')

    # Final Result
    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('Goal succeeded!')
    elif result == TaskResult.CANCELED:
        print('Goal was canceled!')
    elif result == TaskResult.FAILED:
        print('Goal failed!')

    rclpy.shutdown()

if __name__ == '__main__':
    main()
