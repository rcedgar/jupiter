#!/bin/bash -e

name=SRR12063536_length_442

python3 ../py/jupiter_ps2tsv.py $name.ps > $name.tsv

python3 ../py/jupiter_tsv2svg.py $name.tsv > $name.svg

python3 ../py/jupiter_tsv2svg.py $name.tsv config.tsv > $name.config.svg

ls -lh *.svg
