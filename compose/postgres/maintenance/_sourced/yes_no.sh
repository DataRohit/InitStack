#!/usr/bin/env bash

# Yes/No Function
yes_no() {
    # Declare Description
    declare desc="Prompt For Confirmation. \$\"\{1\}\": Confirmation Message."

    # Declare Arguments
    local arg1="${1}"

    # Declare Response
    local response=

    # Prompt For Confirmation
    read -r -p "${arg1} (y/[n])? " response

    # Check Response
    if [[ "${response}" =~ ^[Yy]$ ]]
    then
        # Return True
        return 0
    else
        # Return False
        return 1
    fi
}
