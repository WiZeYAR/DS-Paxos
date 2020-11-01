#!/usr/bin/env bash

echo "Test run with 1000 proposed values"

./run.sh . 1000 0.0 20 1 0

./check_results.py 2 2