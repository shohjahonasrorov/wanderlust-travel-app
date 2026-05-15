#!/bin/bash
# Wanderlust Travel App — Mac/Linux Launcher

# Check Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed."
    echo "Install it from https://www.python.org/downloads/ and re-run this script."
    exit 1
fi

# Install dependencies
pip3 install -r requirements.txt --quiet

# Launch app
python3 wanderlust_app.py
