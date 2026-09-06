cmake_minimum_required(VERSION 3.5)

set(ALGLIB_VERSION "" CACHE STRING "The package version")

project(alglib
    VERSION ${ALGLIB_VERSION}
    LANGUAGES CXX
)

include(GNUInstallDirs)

file(GLOB_RECURSE HDR RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} src/*.h)
file(GLOB_RECURSE SRC RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} src/*.cpp)

add_library(alglib SHARED ${SRC})
set_target_properties(alglib PROPERTIES
    SOVERSION ${PROJECT_VERSION}
    VERSION ${PROJECT_VERSION}
)
target_include_directories(alglib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
)

install(TARGETS alglib)
install(FILES ${HDR} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/alglib)

enable_testing()

foreach(test IN ITEMS
    test_c
    test_i
    # test_x
)
    add_executable(${test} tests/${test}.cpp)
    target_compile_definitions(${test} PRIVATE
        AE_USE_ALLOC_COUNTER
        AE_DEBUG4POSIX
    )
    target_link_libraries(${test} PRIVATE alglib)
    add_test(NAME ${test}
        COMMAND ${test}
    )
endforeach()
