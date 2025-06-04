from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

# This launch file only launches the lidar and the base controller

def generate_launch_description():
    base_pkg = FindPackageShare('bender_base')
    sensor_pkg = FindPackageShare('bender_sensors')
    
    rosaria2_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                base_pkg,
                'launch',
                'rosaria2.launch.py'
            ])
        )
    )
    urg_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                sensor_pkg,
                'launch',
                'lidar',
                'rplidar',
                'rplidar_c1_launch.py'
            ])
        )
    )
    laser_filter = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                sensor_pkg,
                'launch',
                'lidar',
                'filter',
                'laser_filter.launch.py'
            ])
        )
    )
    
    
    

    return LaunchDescription([
        urg_node,
        rosaria2_node,
    ])




