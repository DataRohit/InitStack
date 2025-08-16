#!/usr/bin/env bash

# Newline Function
message_newline() {
    # Declare Description
    echo
}

# Debug Message Function
message_debug()
{
    # Declare Description
    echo -e "DEBUG: ${@}"
}

# Welcome Message Function
message_welcome()
{
    # Declare Description
    echo -e "\e[1m${@}\e[0m"
}

# Warning Message Function
message_warning()
{
    # Declare Description
    echo -e "\e[33mWARNING\e[0m: ${@}"
}

# Error Message Function
message_error()
{
    # Declare Description
    echo -e "\e[31mERROR\e[0m: ${@}"
}

# Info Message Function
message_info()
{
    # Declare Description
    echo -e "\e[37mINFO\e[0m: ${@}"
}

# Suggestion Message Function
message_suggestion()
{
    # Declare Description
    echo -e "\e[33mSUGGESTION\e[0m: ${@}"
}

# Success Message Function
message_success()
{
    # Declare Description
    echo -e "\e[32mSUCCESS\e[0m: ${@}"
}
