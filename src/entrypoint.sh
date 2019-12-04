#!/bin/bash

if [ -z "${MODE}" ]; then
    echo "MODE not set, defaulting to cards"
    MODE="cards"
else 
    MODE="${MODE}"
fi

if [ -z "${NUMBER_OF_CARDS}" ]; then
    echo "NUMBER_OF_CARDS not set, defaulting to 1"
    NUMBER_OF_CARDS="1"
else 
    NUMBER_OF_CARDS="${NUMBER_OF_CARDS}"
fi

python3 treasure_cruise.py $MODE $NUMBER_OF_CARDS

