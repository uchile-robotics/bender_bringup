from launch import LaunchDescription
from launch_ros.actions import LifecycleNode
from ament_index_python.packages import get_package_share_directory
import os
from launch.actions import ExecuteProcess, TimerAction


def generate_launch_description():
    # Rutas base
    bringup_pkg = get_package_share_directory('bender_bringup')
    
    # Archivo de parámetros
    params_file = os.path.join(bringup_pkg, 'params', 'maps', 'maps.yaml')

    # Ruta absoluta del archivo del mapa
    map_yaml_file = os.path.join(bringup_pkg, 'maps', 'stage_5_may_2025.yaml')

    # Nodo map_server como lifecycle node
    map_server_node = LifecycleNode(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        namespace='',
        output='screen',
        parameters=[
            params_file,
            {'yaml_filename': map_yaml_file}  # Sobrescribe el parámetro del archivo de mapa
        ]
    )



    return LaunchDescription([
        map_server_node
    ])
