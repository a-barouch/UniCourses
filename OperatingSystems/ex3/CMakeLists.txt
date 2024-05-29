cmake_minimum_required(VERSION 3.11)
project(OS_ex3)

set(CMAKE_CXX_STANDARD 14)

add_executable(OS_ex3 Barrier.cpp Barrier.h MapReduceFramework.cpp MapReduceFramework.h MapReduceClient.h SampleClient.cpp)

SET(CMAKE_CXX_FLAGS -pthread)