#!/bin/bash

if [ -z "${MODE}" ]; then
    echo "MODE not set, defaulting to cards"
    MODE="cards"
else 
    MODE="${MODE}"
fi

if [ -z "${PRINT_ID_RANGE}" ]; then
    echo "PRINT_ID_RANGE not set, defaulting to 1-2"
    PRINT_ID_RANGE="1-2"
else 
    PRINT_ID_RANGE="${PRINT_ID_RANGE}"
fi

python3 treasure_cruise.py $MODE $PRINT_ID_RANGE

