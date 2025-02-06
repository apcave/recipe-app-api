#!/bin/bash
# Create a virtual environment
python3 -m venv ~/venv

# Activate the virtual environment
source ~/venv/bin/activate

# Install the required packages
pip install -r requirements.txt
pip install -r requirements.dev.txt

cd app
flake8 .