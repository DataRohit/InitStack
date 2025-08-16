#!/usr/bin/env bash

# Countdown Function
countdown() {
    # Declare Description
    declare desc="A Simple Countdown"

    # Declare Parameters
    local seconds="${1}"

    # Calculate End Time
    local d=$(($(date +%s) + "${seconds}"))

    # Countdown Loop
    while [ "$d" -ge `date +%s` ]; do
        # Print Remaining Time
        echo -ne "$(date -u --date @$(($d - `date +%s`)) +%H:%M:%S)\r";

        # Sleep For 100ms
        sleep 0.1
    done
}
