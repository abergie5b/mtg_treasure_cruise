#!/bin/bash

if test -f "/treasure_cruise/data/AllPrintings.sqlite"; then
    echo "AllPrintings.sqlite already exists, skipping download"
else
    echo "Downloading AllPrintings.sqlite"
    wget https://www.mtgjson.com/files/AllPrintings.sqlite -qP /treasure_cruise/data
fi

exec jupyter notebook

