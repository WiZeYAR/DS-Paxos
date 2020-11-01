#!/usr/bin/env bash

echo "Test run with 100 proposed values and 10% package loss rate"

./run.sh . 100 0.1 10 0 0

./check_results.py 2 2 true