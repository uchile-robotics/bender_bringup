from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    bringup_pkg = FindPackageShare('jaime_bringup')
    description_pkg = FindPackageShare('jaime_description')

    display_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                description_pkg, 'launch', 'display.launch.py'
            ])
        )
    )

    basic_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                bringup_pkg, 'launch', 'robot', 'jaime_basic.launch.py'
            ])
        )
    )

    localization_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                bringup_pkg, 'launch', 'localization', 'slam_toolbox.launch.py'
            ])
        )
    )

    navigation_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                bringup_pkg, 'launch', 'navigation', 'navigation_launch.py'
            ])
        )
    )

    # Timer para lanzar localización después de 5s
    launch_localization = TimerAction(
        period=5.0,
        actions=[localization_node]
    )

    # Timer para lanzar navegación después de 10s
    launch_navigation = TimerAction(
        period=10.0,
        actions=[navigation_node]
    )

    return LaunchDescription([
        display_node,
        basic_node,
        launch_localization,
        launch_navigation,
    ])
