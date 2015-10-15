#!/bin/bash

python tour.py index.mustache > site/index.html
python tour.py results.mustache > results.csv
