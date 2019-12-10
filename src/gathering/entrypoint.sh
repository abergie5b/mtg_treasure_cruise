#!/bin/bash

if [ -z "${CARD_ID_RANGE}" ]; then
    echo "CARD_ID_RANGE not set, defaulting to 1-2"
    CARD_ID_RANGE="1-2"
else 
    CARD_ID_RANGE="${CARD_ID_RANGE}"
fi

if test -f "/treasure_cruise/data/AllPrintings.sqlite"; then
    echo "AllPrintings.sqlite already exists, skipping download"
else
    echo "Downloading AllPrintings.sqlite"
    wget https://www.mtgjson.com/files/AllPrintings.sqlite -qP /treasure_cruise/data
fi

if test -f "./treasure_cruise.log"; then
    echo "treasure_cruise.log already exists, skipping creation"
else
    touch treasure_cruise.log
    echo "Created treasure_cruise.log for logger output"
fi

python3 treasure_cruise.py $CARD_ID_RANGE

