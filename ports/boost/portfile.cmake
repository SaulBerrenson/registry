
string(REPLACE "." "-" ARCHIVE_VERSION ${VERSION})

set(BOOST_ARVHICE_FILENAME boost-${ARCHIVE_VERSION}.zip)

vcpkg_download_distfile(
    ARCHIVE_ZIP
    URLS https://github.com/boostorg/boost/releases/download/boost-${VERSION}/boost-${VERSION}-cmake.7z
    FILENAME ${BOOST_ARVHICE_FILENAME}
    SHA512 994356c84f4b96e263087eff40e53298791e7d72c6d24dd2cc3988c32edaa880180d39401504befe5c1b197ebead77c855452c608c6560a42f50f5a3016e0add
)

vcpkg_extract_source_archive(
    SOURCE_PATH
    ARCHIVE "${ARCHIVE_ZIP}"
)

string(COMPARE EQUAL "${VCPKG_LIBRARY_LINKAGE}" "dynamic" BUILD_SHARED)
string(COMPARE EQUAL "${VCPKG_CRT_LINKAGE}" "static" BUILD_STATIC_CRT)

if(BUILD_SHARED)
    set(OPTION_BUILD_SHARED_LIBS ON)
else()
    set(OPTION_BUILD_SHARED_LIBS OFF)
endif()

if(BUILD_STATIC_CRT)
    set(BOOST_RUNTIME_LINK static)
else()
    set(BOOST_RUNTIME_LINK shared)
endif()


if("force-static" IN_LIST FEATURES)
    set(OPTION_BUILD_SHARED_LIBS OFF) #rewrite options
    vcpkg_check_linkage(ONLY_STATIC_LIBRARY)
endif()

if("force-shared" IN_LIST FEATURES)
    set(OPTION_BUILD_SHARED_LIBS ON) #rewrite options
    vcpkg_check_linkage(ONLY_DYNAMIC_LIBRARY)
endif()


set(BOOST_EXCLUDE_COMPONENTS test log wave stacktrace python)
list(JOIN BOOST_EXCLUDE_COMPONENTS "\\;" BOOST_EXCLUDE_LIBRARIES)

message(STATUS "Replace BoostConfig with fixed search lib_DIR")
configure_file(${CMAKE_CURRENT_LIST_DIR}/BoostConfig.cmake.in ${SOURCE_PATH}/tools/cmake/config/BoostConfig.cmake USE_SOURCE_PERMISSIONS @ONLY)

# disable check LINUX_VERSION_CODE in ASTRA
if(UNIX)    
    file(COPY_FILE ${CMAKE_CURRENT_LIST_DIR}/config.hpp ${SOURCE_PATH}/libs/asio/include/boost/asio/detail/config.hpp)
endif()

message(STATUS "Building boost with BUILD_SHARED_LIBS=${OPTION_BUILD_SHARED_LIBS}, CRT=${BOOST_RUNTIME_LINK} EXCLUDE:${BOOST_EXCLUDE_COMPONENTS}")

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
    WINDOWS_USE_MSBUILD
    OPTIONS
        -DBUILD_SHARED_LIBS=${OPTION_BUILD_SHARED_LIBS}
        -DBOOST_RUNTIME_LINK=${BOOST_RUNTIME_LINK}
        -DBOOST_EXCLUDE_LIBRARIES=${BOOST_EXCLUDE_LIBRARIES}
        -DBOOST_ENABLE_PYTHON=OFF
        -DBUILD_TESTING=OFF
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(PACKAGE_NAME boost CONFIG_PATH lib/cmake/Boost-${VERSION} DO_NOT_DELETE_PARENT_CONFIG_PATH) #main config

vcpkg_copy_pdbs()

# Fixup configs for debug and release
function(_fixup_boost_config_for_dir_ target_dir)

    message(STATUS "Fixup boost configs for dir: ${target_dir}")
    file(GLOB CONFIG_LIST LIST_DIRECTORIES true ${target_dir}/boost_*)

    foreach(dir ${CONFIG_LIST})
        IF(IS_DIRECTORY ${dir})

            string(REPLACE "${target_dir}/" "" dir_name "${dir}")
            #string(REPLACE "-1.83.0" "" PKG_CONFIG_NAME ${dir_name})
            string(REPLACE "-${VERSION}" "" PKG_CONFIG_NAME ${dir_name})
            message(STATUS "try fixup: ${dir_name} - ${PKG_CONFIG_NAME}")

            vcpkg_cmake_config_fixup(PACKAGE_NAME ${PKG_CONFIG_NAME} CONFIG_PATH lib/cmake/${dir_name} DO_NOT_DELETE_PARENT_CONFIG_PATH)
        ELSE()
            CONTINUE()
        ENDIF()
    endforeach()

    unset(CONFIG_LIST)
endfunction()

_fixup_boost_config_for_dir_(${CURRENT_PACKAGES_DIR}/debug/lib/cmake)
_fixup_boost_config_for_dir_(${CURRENT_PACKAGES_DIR}/lib/cmake)

file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/lib/cmake") 
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/lib/cmake") 

file(INSTALL "${SOURCE_PATH}/LICENSE_1_0.txt" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
