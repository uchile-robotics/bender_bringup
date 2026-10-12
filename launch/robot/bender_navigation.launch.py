from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

# launch that runs nav2 and slam stuff

def generate_launch_description():
    bringup_pkg = FindPackageShare('bender_bringup')

    slam = LaunchConfiguration('slam')
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_slam = DeclareLaunchArgument(
        'slam', default_value='false',
        description='Build a map with slam_toolbox instead of localizing with AMCL'
    )
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )

    localization_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                bringup_pkg, 'launch', 'localization', 'localization_launch.py'
            ])
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
        condition=UnlessCondition(slam)
    )

    slam_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                bringup_pkg, 'launch', 'localization', 'slam_toolbox.launch.py'
            ])
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
        condition=IfCondition(slam)
    )

    navigation_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                bringup_pkg, 'launch', 'navigation', 'navigation_launch.py'
            ])
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    return LaunchDescription([
        declare_slam,
        declare_use_sim_time,
        localization_node,
        slam_node,
        navigation_node,
    ])
