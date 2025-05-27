from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

# This launch file only launches the lidar and the base controller

def generate_launch_description():
    base_pkg = FindPackageShare('bender_bringup')
    sensor_pkg = FindPackageShare('bender_sensors')
    urg_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                sensor_pkg,
                'launch',
                'lidar',
                'hokuyo',
                'hokuyo.launch.py'
            ])
        )
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
    
    

    return LaunchDescription([
        rosaria2_node,
        urg_node,
    ])




