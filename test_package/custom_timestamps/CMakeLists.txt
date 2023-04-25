cmake_minimum_required(VERSION 3.15)
cmake_policy(SET CMP0074 NEW)

project(custom_timestamps)
include(GNUInstallDirs)

find_package(uvgrtp REQUIRED CONFIG)
add_executable(${PROJECT_NAME} custom_timestamps.cpp)
target_link_libraries(${PROJECT_NAME} uvgrtp::uvgrtp)

set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD_REQUIRED ON
    CXX_STANDARD 17
    POSITION_INDEPENDENT_CODE ON
)

install(
    TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
)
