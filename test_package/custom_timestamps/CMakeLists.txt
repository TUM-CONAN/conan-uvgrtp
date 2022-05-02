# Copyright (c) 2020 by Robert Bosch GmbH. All rights reserved.
# Copyright (c) 2021 by Apex.AI Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

# Build singleprocess example
cmake_minimum_required(VERSION 3.16)
project(example_custom_timestamps)

include(GNUInstallDirs)

find_package(uvgrtp REQUIRED)


add_executable(custom_timestamps ./custom_timestamps.cpp)
target_link_libraries(custom_timestamps
    CONAN_PKG::uvgrtp
)
set_target_properties(custom_timestamps PROPERTIES
    CXX_STANDARD_REQUIRED ON
    CXX_STANDARD 17
    POSITION_INDEPENDENT_CODE ON
)


install(
    TARGETS custom_timestamps
    RUNTIME DESTINATION bin
)
