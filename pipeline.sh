#!/usr/bin/env bash

python3 run.py load_clean
python3 run.py features
python3 run.py train
python3 run.py score
python3 run.py evaluate
python3 run.py create_database
python3 run.py populate_database
