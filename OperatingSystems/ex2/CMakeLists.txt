cmake_minimum_required(VERSION 3.12)
project(os_ex2)

set(CMAKE_CXX_STANDARD 14)

add_library(uthreads uthreads.h uthreads.cpp Thread.cpp Thread.h)

add_executable(os_ex2 uthreads.cpp uthreads.h Thread.cpp Thread.h)

add_subdirectory(tests)

