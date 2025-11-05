from launch import LaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg = get_package_share_directory('jaime_bringup')
    cartographer_config_dir = os.path.join(
        pkg,
        'params',
        'localization',
        'cartographer',
    )
    cartographer_config_file = 'cartographer_config.lua'

    return LaunchDescription([
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            parameters=[{
                'use_sim_time': False,
            }],
            arguments=[
                '-configuration_directory', cartographer_config_dir,
                '-configuration_basename', cartographer_config_file
            ]
        ),

        # Nodo de occupancy grid
        Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='cartographer_occupancy_grid_node',
            output='screen',
            parameters=[{
                'resolution': 0.05,
                'publish_period_sec': 1.0
            }]
        )
    ])
