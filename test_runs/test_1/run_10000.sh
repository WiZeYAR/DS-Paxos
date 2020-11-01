#!/usr/bin/env bash

echo "Test run with 10000 proposed values for up to 2 minutes; unlikely to terminate in time (termination < 100%)"


./run.sh . 10000 0.0 120 1 0

./check_results.py 2 2