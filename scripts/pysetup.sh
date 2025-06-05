#!/usr/bin/env bash

PYTHON_ENV=$1

python3 -m venv ./$PYTHON_ENV  \
        && export PATH=./$PYTHON_ENV/bin:$PATH \
        && echo "source ./$PYTHON_ENV/bin/activate" >> ~/.bashrc

source ./$PYTHON_ENV/bin/activate

pip3 install -r requirements.txt
