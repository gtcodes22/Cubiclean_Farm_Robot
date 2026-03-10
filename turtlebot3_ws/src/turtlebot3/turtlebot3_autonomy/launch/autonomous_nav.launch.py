import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_tb3_nav2 = get_package_share_directory('turtlebot3_navigation2')
    pkg_autonomy = get_package_share_directory('turtlebot3_autonomy')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if true'
    )

    map_file_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_autonomy, 'maps', 'map.yaml'),
        description='Full path to map yaml'
    )

    waypoints_file_arg = DeclareLaunchArgument(
        'waypoints_file',
        default_value=os.path.join(pkg_autonomy, 'config', 'waypoints.yaml'),
        description='Full path to waypoints yaml'
    )

    use_sim_time   = LaunchConfiguration('use_sim_time')
    map_file       = LaunchConfiguration('map')
    waypoints_file = LaunchConfiguration('waypoints_file')

    # Use the official TurtleBot3 navigation2 launch instead of raw nav2_bringup.
    # This loads burger-specific Nav2 params and the correct RViz config.
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_tb3_nav2, 'launch', 'navigation2.launch.py')
        ),
        launch_arguments={
            'map': map_file,
            'use_sim_time': use_sim_time,
        }.items()
    )

    mission_node = Node(
        package='turtlebot3_autonomy',
        executable='waypoint_mission',
        name='waypoint_mission',
        parameters=[{
            'use_sim_time': use_sim_time,
            'waypoints_file': waypoints_file,
        }],
        output='screen'
    )

    monitor_node = Node(
        package='turtlebot3_autonomy',
        executable='robot_monitor',
        name='robot_monitor',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time_arg,
        map_file_arg,
        waypoints_file_arg,
        nav2_launch,
        mission_node,
        monitor_node,
    ])
