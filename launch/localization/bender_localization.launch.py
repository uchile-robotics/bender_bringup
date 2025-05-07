from launch import LaunchDescription
from launch_ros.actions import Node, LifecycleNode
from ament_index_python.packages import get_package_share_directory
import os
from launch.actions import ExecuteProcess, TimerAction


def generate_launch_description():
    # Rutas base
    bringup_pkg = get_package_share_directory('bender_bringup')
    
    amcl_params = os.path.join(bringup_pkg, 'params', 'localization', 'amcl.yaml')
    map_params = os.path.join(bringup_pkg, 'params', 'maps', 'maps.yaml')

    map_yaml_file = os.path.join(bringup_pkg, 'maps', 'stage_5_may_2025.yaml')

    map_server_node = LifecycleNode(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        namespace='',
        output='screen',
        parameters=[
            map_params,
            {'yaml_filename': map_yaml_file} 
        ]
    )
    amcl_node = LifecycleNode(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        namespace='',
        output='screen',
        parameters=[amcl_params],
    )
    
    

    return LaunchDescription([
        map_server_node,
        amcl_node
    ])



