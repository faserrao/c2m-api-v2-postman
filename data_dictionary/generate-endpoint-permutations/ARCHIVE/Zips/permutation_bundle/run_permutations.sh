#!/bin/bash
set -e
if [ "$1" == "--interactive" ]; then
  python3 permutation_generator.py --interactive
else
  python3 permutation_generator.py
fi
