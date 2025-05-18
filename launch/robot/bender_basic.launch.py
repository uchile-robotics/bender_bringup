from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

import os

def generate_launch_description():
    urg_node_dir = FindPackageShare('urg_node2')
    bringup_pkg = FindPackageShare('bender_bringup')

    base_params = PathJoinSubstitution([
        bringup_pkg,
        'params',
        'robot',
        'pioneer.yaml'
    ])
    urg_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                urg_node_dir,
                'launch',
                'urg_node2.launch.py'
            ])
        )
    )

    

    rosaria2_node = Node(
        package='rosaria2',
        executable='rosaria2_node',
        name='rosaria2',
        output='screen',
        parameters=[base_params]
    )

    
    

    return LaunchDescription([
        rosaria2_node,
        urg_node,
    ])




