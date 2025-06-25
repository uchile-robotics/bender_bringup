from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
import os
# This launch file launches the lidar, the base controller and a teleop node

def generate_launch_description():
    base_pkg = FindPackageShare('bender_base')
    sensor_pkg = FindPackageShare('bender_sensors')
    twist_mux_params = os.path.join(
        os.get_package_share_directory('bender_sensors'),
        'params',
        'joy',
        'twist_mux.yaml'
    )
    
    rosaria2_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                base_pkg,
                'launch',
                'rosaria2.launch.py'
            ])
        )
    )
    lidar_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                sensor_pkg,
                'launch',
                'lidar',
                'rplidar_c1_launch.py'
            ])
        )
    )
    
    joy_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                sensor_pkg,
                'launch',
                'joy',
                'joystick.launch.py'
            ])
        )
    ) 

    twist_mux = Node(
            package="twist_mux",
            executable="twist_mux",
            parameters=[twist_mux_params],
            remappings=[('/cmd_vel_out','/diff_cont/cmd_vel_unstamped')] # TODO: check base topic in order to do correct remapping
        )
    return LaunchDescription([
        lidar_node,
        rosaria2_node,
        joy_node,
        twist_mux
    ])




