from launch import LaunchDescription
from launch_ros.actions import LifecycleNode, Node
from launch.actions import ExecuteProcess, TimerAction
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    config_path = os.path.join(
        get_package_share_directory('urg_node2'),
        'config',
        'params_serial.yaml'
    )
    rosaria2_node = Node(
        package='rosaria2',
        executable='rosaria2_node',
        name='rosaria2',
        output='screen',
    )

    laser_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0.15', '0', '0.2', '0', '0', '0', 'base_link', 'laser'],
        output='screen',
    )
    # Nodo lifecycle
    urg_node = LifecycleNode(
        package='urg_node2',
        executable='urg_node2_node',
        name='urg_node2',
        namespace='',  # Se añade el namespace vacío
        output='screen',
        parameters=[config_path]
    )

    # Comando para configurar el nodo
    configure_cmd = ExecuteProcess(
        cmd=['ros2', 'lifecycle', 'set', '/urg_node2', 'configure'],
        output='screen'
    )

    # Comando para activar el nodo
    activate_cmd = ExecuteProcess(
        cmd=['ros2', 'lifecycle', 'set', '/urg_node2', 'activate'],
        output='screen'
    )

    return LaunchDescription([
        urg_node,
        TimerAction(period=0.1, actions=[configure_cmd]),
        TimerAction(period=0.2, actions=[activate_cmd]),
        rosaria2_node,
        laser_tf
    ])




