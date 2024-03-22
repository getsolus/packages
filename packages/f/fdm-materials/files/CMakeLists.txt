project(fdm-materials NONE)

cmake_minimum_required(VERSION 2.8.12)

include(CMakePackageConfigHelpers)

option(EMBEDDED "Build for Ultimaker Embedded software" OFF)

if(NOT EMBEDDED)
    set(INSTALL_PATH "share/cura/resources/materials"
        CACHE PATH
        "The path to install the materials to. Should ideally be relative to CMAKE_INSTALL_PREFIX"
        )
else()
    # Then we're cmaking for Jedi
    set(INSTALL_PATH "share/fdm_materials"
        CACHE STRING
        "Destination to install the materials to. Should be relative to CMAKE_INSTALL_PREFIX")

    if(IS_ABSOLUTE ${INSTALL_PATH})
        set(INSTALL_PATH ${INSTALL_PATH})
    else()
        set(INSTALL_PATH ${CMAKE_INSTALL_PREFIX}/${INSTALL_PATH})
    endif()
endif()

file(GLOB _files *.fdm_material *.sig)

# Determine version number
find_package(Git)

if (DEFINED ENV{GITHUB_ACTIONS})
    set(CPACK_PACKAGE_VERSION "${GIT_VERSION}+$ENV{GITHUB_SHA}")
endif()

install(FILES ${_files} DESTINATION ${INSTALL_PATH})

include(CPackConfig.cmake)
