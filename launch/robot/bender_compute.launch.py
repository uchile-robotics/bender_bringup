from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

# launch for the computer on top of bender: Nav2 and MoveIt only.
# The hardware (ros2_control, lidar, joystick, twist_mux) runs on the raspi
# with bender_hardware.launch.py; do not launch it here too.


def include_robot_launch(launch_file, launch_arguments, condition=None):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('bender_bringup'), 'launch', 'robot', launch_file
            ])
        ),
        launch_arguments=launch_arguments.items(),
        condition=condition
    )


def generate_launch_description():
    use_arms = LaunchConfiguration('use_arms')
    use_base = LaunchConfiguration('use_base')
    use_rviz = LaunchConfiguration('use_rviz')
    slam = LaunchConfiguration('slam')

    declare_use_arms = DeclareLaunchArgument(
        'use_arms', default_value='true',
        description='Start MoveIt (move_group). Needs use_arms:=true on the raspi'
    )
    declare_use_base = DeclareLaunchArgument(
        'use_base', default_value='true',
        description='Start localization and Nav2. Needs use_base:=true on the raspi'
    )
    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz', default_value='true',
        description='Launch MoveIt RViz (only if use_arms is true)'
    )
    declare_slam = DeclareLaunchArgument(
        'slam', default_value='false',
        description='Build a map with slam_toolbox instead of localizing with AMCL'
    )

    navigation = include_robot_launch(
        'bender_navigation.launch.py',
        {'slam': slam},
        condition=IfCondition(use_base)
    )

    # use_base le dice a MoveIt si la base está corriendo en la raspi: en ese caso
    # base_link cuelga de odom y no se publica el TF estático world -> base_link.
    moveit = include_robot_launch(
        'bender_moveit.launch.py',
        {'use_rviz': use_rviz, 'use_base': use_base},
        condition=IfCondition(use_arms)
    )

    return LaunchDescription([
        declare_use_arms,
        declare_use_base,
        declare_use_rviz,
        declare_slam,
        navigation,
        moveit,
    ])
