#!/bin/bash

conda env create -f selenium_env.yml
eval "$(conda shell.bash hook)"
conda activate selenium_env
