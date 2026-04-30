import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # Obtener el directorio del paquete bender_description para los launch files
    bender_description_dir = get_package_share_directory('bender_description')

    # 1. ros2 run bender_manipulation dynamixel_node.py
    dynamixel_node = Node(
        package='bender_manipulation',
        executable='dynamixel_node.py',
        name='dynamixel_node',
        output='screen'
    )

    # 2. ros2 run bender_manipulation dynamixel_trajectory_bridge.py
    dynamixel_trajectory_bridge = Node(
        package='bender_manipulation',
        executable='dynamixel_trajectory_bridge.py',
        name='dynamixel_trajectory_bridge',
        output='screen'
    )
    serial_encoder_node = Node(
        package='bender_manipulation',
        executable='serial_encoder_node',
        name='serial_encoder_node',
        output='screen'
    )

    shoulder_control = Node(
        package='bender_manipulation',
        executable='shoulder_control.py',
        name='shoulder_controller_node',
        output='screen'
    )
    odrive_node = Node(
        package='bender_manipulation',
        executable='oddrive.py',
        name='odrive_velocity_node',
        output='screen'
    )


    bender_moveit = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bender_description_dir, 'launch', 'bender_moveit.launch.py')
        )
    )

    # Agregamos todo a la descripción del lanzamiento
    return LaunchDescription([
        dynamixel_node,
        dynamixel_trajectory_bridge,
        bender_moveit,
        serial_encoder_node,
        odrive_node,
        shoulder_control
    ])
