#!/bin/bash

python -m venv backend
source backend/bin/activate
python -m pip install --upgrade pip
pip install fastapi uvicorn

