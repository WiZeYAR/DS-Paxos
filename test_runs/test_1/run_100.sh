#!/usr/bin/env bash

echo "Test run with 100 proposed values"

./run.sh . 100 0.0 10 1 0

./check_results.py 2 2 true