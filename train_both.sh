#!/bin/bash
python src/agent/train_sum_of_square.py &
python src/agent/train_constant.py &
wait
