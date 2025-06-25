from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

# This launch runs the same as the bender_basic launch and launches also Bender's TF
# also launches the localization and navigation, so it centralizes it to a single
# launch file
def generate_launch_description():
    bringup_pkg = FindPackageShare('bender_bringup')
    description_pkg = FindPackageShare('bender_description')


    display_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                description_pkg,
                'launch',
                'display.launch.py'

            ])
        )
    )
 
    basic_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                bringup_pkg,
                'launch',
                'robot',
                'bender_basic.launch.py'
            ])
        )
    )
 
    return LaunchDescription([
        display_node,
        basic_node,
    ])




