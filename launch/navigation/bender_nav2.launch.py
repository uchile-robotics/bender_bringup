from launch import LaunchDescription
from launch_ros.actions import Node, LifecycleNode
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
import os



def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_subscribe_transient_local = LaunchConfiguration('map_subscribe_transient_local')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )
    bringup_pkg = FindPackageShare('bender_bringup')

    bender_localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                bringup_pkg,
                'launch',
                'localization',
                'bender_localization.launch.py'
            ])
        )
    )
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_map_subscribe_transient_local = DeclareLaunchArgument(
        'map_subscribe_transient_local',
        default_value='true',
        description='Use transient local subscription for map'
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('nav2_bringup'),
            '/launch/navigation_launch.py'
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map_subscribe_transient_local': map_subscribe_transient_local,
        }.items()
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_map_subscribe_transient_local,
        nav2_launch,
        bender_localization
    ])
