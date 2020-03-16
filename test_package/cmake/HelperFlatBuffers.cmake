# USAGE:
# generate_flatbuffers("MasterMessage_gen"
#     TARGET ${PROJECT_NAME}_lib
#     FILES "${CMAKE_CURRENT_SOURCE_DIR}/examples/flatbuffers/MasterMessage.fbs"
#     OUTPATH "${ROOT_PROJECT_DIR}/examples/webclient/src/generated/flatbuffers"
#     EXTRA_ARGS "--ts;--no-fb-import;--short-names"
#     DEBUG)
#
# add_executable(testme
#     ${strawpoll_gen_OUTPUTS} # generated by flatc
#     main.cpp
# )

find_program(flatc flatc NO_SYSTEM_ENVIRONMENT_PATH NO_CMAKE_SYSTEM_PATH)
message(STATUS "find_program for flatc: ${flatc}")

if(${flatc} STREQUAL "")
    message(FATAL_ERROR "flatc not found ${flatc}")
endif()

MACRO(PARSE_ARGUMENTS prefix arg_names option_names)
    SET(DEFAULT_ARGS)
    FOREACH(arg_name ${arg_names})
        SET(${prefix}_${arg_name})
    ENDFOREACH(arg_name)
    FOREACH(option ${option_names})
        SET(${prefix}_${option} FALSE)
    ENDFOREACH(option)

    SET(current_arg_name DEFAULT_ARGS)
    SET(current_arg_list)
    FOREACH(arg ${ARGN})
        SET(larg_names ${arg_names})
        LIST(FIND larg_names "${arg}" is_arg_name)
        IF (is_arg_name GREATER -1)
            SET(${prefix}_${current_arg_name} ${current_arg_list})
            SET(current_arg_name ${arg})
            SET(current_arg_list)
        ELSE (is_arg_name GREATER -1)
            SET(loption_names ${option_names})
            LIST(FIND loption_names "${arg}" is_option)
            IF (is_option GREATER -1)
                SET(${prefix}_${arg} TRUE)
            ELSE (is_option GREATER -1)
                SET(current_arg_list ${current_arg_list} ${arg})
            ENDIF (is_option GREATER -1)
        ENDIF (is_arg_name GREATER -1)
    ENDFOREACH(arg)
    SET(${prefix}_${current_arg_name} ${current_arg_list})
ENDMACRO(PARSE_ARGUMENTS)

# NOTE: you can set multiple EXTRA_ARGS like so "--ts;--no-fb-import;--short-names"
function(generate_flatbuffers Name)

    # argument parsing
    PARSE_ARGUMENTS(ARG "TARGET;FILES;OUTPATH;EXTRA_ARGS;EXPORT_MACRO" "DEBUG" ${ARGN})

    IF(NOT ARG_TARGET)
        MESSAGE(SEND_ERROR "Error: PROTOBUF_GENERATE_CPP() called without any targets")
        RETURN()
    ENDIF(NOT ARG_TARGET)

    IF(NOT ARG_FILES)
        MESSAGE(SEND_ERROR "Error: PROTOBUF_GENERATE_CPP() called without any proto files")
        RETURN()
    ENDIF(NOT ARG_FILES)

    SET(OUTPATH ${ARG_OUTPATH})
    IF(OUTPATH_LENGTH EQUAL 1)
        SET(OUTPATH ${CMAKE_CURRENT_BINARY_DIR})
    ENDIF()

    IF(ARG_DEBUG)
        MESSAGE("OUTPATH: ${OUTPATH}")
    ENDIF()

    set(FLATC_OUTPUTS)
    foreach(FILE ${ARG_FILES})
        get_filename_component(FLATC_OUTPUT ${FILE} NAME_WE)
        set(FLATC_OUTPUT
                "${OUTPATH}/${FLATC_OUTPUT}_generated.h")
        list(APPEND FLATC_OUTPUTS ${FLATC_OUTPUT})

        IF(ARG_DEBUG)
            MESSAGE("FLATC_OUTPUT: ${FLATC_OUTPUT}")
        ENDIF()

        GET_FILENAME_COMPONENT(ABS_FILE ${FILE} ABSOLUTE)

        IF(ARG_DEBUG)
            MESSAGE("ABS_FILE: ${ABS_FILE}")
        ENDIF()

        IF(ARG_DEBUG)
            MESSAGE("ARG_TARGET: ${ARG_TARGET}")
        ENDIF()


        # NOTE: regen files at configure step
        execute_process(
            COMMAND ${CMAKE_COMMAND} -E make_directory ${OUTPATH}
        )

        execute_process(
            COMMAND ${flatc} ${ARG_EXTRA_ARGS} -o "${OUTPATH}" "${ABS_FILE}"
        )

        # NOTE: regen files at build step
        add_custom_command(TARGET "${ARG_TARGET}"
                PRE_BUILD
                COMMAND ${CMAKE_COMMAND} -E make_directory ${OUTPATH}
                COMMAND ${flatc} ${ARG_EXTRA_ARGS} -o "${OUTPATH}" "${ABS_FILE}"
                #ARGS ${ARG_EXTRA_ARGS} "${OUTPATH}" ${ABS_FILE}
                DEPENDS ${ABS_FILE}
                COMMENT "(build) Building flatc header for ${ABS_FILE} with args ${ARG_EXTRA_ARGS}"
                WORKING_DIRECTORY ${OUTPATH}
                VERBATIM # If VERBATIM is given then all arguments to the commands will be escaped properly
        )

        SET_SOURCE_FILES_PROPERTIES(${FLATC_OUTPUT} PROPERTIES GENERATED TRUE)
    endforeach()
    set(${Name}_OUTPUTS ${FLATC_OUTPUTS} PARENT_SCOPE)
endfunction()