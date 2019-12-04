#!/bin/bash

if [ -z "${PRINT_ID_RANGE}" ]; then
    echo "PRINT_ID_RANGE not set, defaulting to 1-2"
    PRINT_ID_RANGE="1-2"
else 
    PRINT_ID_RANGE="${PRINT_ID_RANGE}"
fi

python3 treasure_cruise.py $PRINT_ID_RANGE

