cmake_minimum_required(VERSION 3.8)
project(bender_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}/
)

install(
  DIRECTORY maps/
  DESTINATION share/${PROJECT_NAME}/maps/
)
install(
  DIRECTORY params/
  DESTINATION share/${PROJECT_NAME}/params/
)
ament_package()
