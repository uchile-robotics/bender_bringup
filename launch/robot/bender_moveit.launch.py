from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import SetParameter
from launch_ros.substitutions import FindPackageShare

# launch that runs moveit stuff

def include_moveit_launch(launch_file, condition=None):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('bender_moveit_config'), 'launch', launch_file
            ])
        ),
        condition=condition
    )


def generate_launch_description():
    use_rviz = LaunchConfiguration('use_rviz')
    use_base = LaunchConfiguration('use_base')
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz', default_value='true',
        description='Launch MoveIt RViz'
    )
    declare_use_base = DeclareLaunchArgument(
        'use_base', default_value='true',
        description='Set to false if the base is not running, to publish the static world -> base_link TF'
    )

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )

    # Con la base andando, base_link ya cuelga de odom (diff drive): publicar además
    # world -> base_link le daría dos padres y rompería el árbol de TF.
    static_virtual_joint_tfs = include_moveit_launch(
        'static_virtual_joint_tfs.launch.py',
        condition=UnlessCondition(use_base)
    )

    move_group = include_moveit_launch('move_group.launch.py')

    moveit_rviz = include_moveit_launch(
        'moveit_rviz.launch.py',
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        declare_use_rviz,
        declare_use_base,
        declare_use_sim_time,
        GroupAction([
            SetParameter('use_sim_time', use_sim_time),
            static_virtual_joint_tfs,
            move_group,
            moveit_rviz,
        ]),
    ])
