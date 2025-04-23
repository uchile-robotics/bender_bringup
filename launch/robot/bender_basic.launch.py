from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='rosaria2',
            executable='rosaria_node',
            name='rosaria2',
            output='screen',
        ),
        Node(
            package='urg_node2',
            executable='urg_node2_node',
            name='urg_node2',
            output='screen',
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0.15', '0', '0.2', '0', '0', '0', 'base_link', 'laser'],
            output='screen',
        ),
    ])
