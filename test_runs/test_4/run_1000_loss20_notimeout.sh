#!/usr/bin/env bash

echo "Test run with 1000 proposed values and 20% package loss rate"

./run.sh . 1000 0.2 20 1 0

./check_results.py 2 2