from launch import LaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Ruta al otro launch
    bender_bringup_dir = get_package_share_directory('bender_bringup')
    basic_launch = os.path.join(bender_bringup_dir, 'launch', 'robot', 'bender_basic.launch.py')

    # Ruta al config de cartographer
    cartographer_config_dir = '/opt/ros/jazzy/share/cartographer/configuration_files'
    cartographer_config_file = 'cartographer_config.lua'

    return LaunchDescription([
        # Incluir tu launch base
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(basic_launch)
        ),

        # Nodo de Cartographer
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            parameters=[{
                'use_sim_time': False,  # o True si estás en simulación
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
