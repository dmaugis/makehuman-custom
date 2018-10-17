cmake_minimum_required(VERSION 3.6)
project( makeskin )
find_package(OpenCV REQUIRED )
find_package(Boost 1.55.0 COMPONENTS filesystem system REQUIRED)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(makeskin_SOURCES	makeskin.cpp)

include_directories(.)
include_directories(${OPENCV_INCLUDE_DIRS})	

add_executable( makeskin ${makeskin_SOURCES} )
target_link_libraries( makeskin ${OpenCV_LIBS} ${Boost_LIBRARIES}   )
install(TARGETS makeskin RUNTIME DESTINATION bin)	


