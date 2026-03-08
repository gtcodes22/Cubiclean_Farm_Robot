from setuptools import setup
import os
from glob import glob

package_name = 'turtlebot3_autonomy'

setup(
    name=package_name,
    version='0.0.1',
    packages=[
        package_name,
        package_name + '.utils',        # required to install the utils subpackage
    ],
    data_files=[
        # ament package index marker — required for ros2 launch to find this package
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install launch files into the share directory
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        # Install config files
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
        # Install map files
        (os.path.join('share', package_name, 'maps'),
            glob('maps/*.yaml') + glob('maps/*.pgm')),
    ],
    install_requires=['setuptools', 'psutil'],
    zip_safe=True,
    maintainer='My Name',
    maintainer_email='myemail@gmail.com',
    description='Autonomous waypoint navigation for TurtleBot3',
    license='Apache 2.0',
    entry_points={
        'console_scripts': [
            'waypoint_mission = turtlebot3_autonomy.waypoint_mission:main',
            'robot_monitor = turtlebot3_autonomy.robot_monitor:main',
        ],
    },
)
