# SLIR-MWSU

This project seeks to simulate disease spread in a student population using a cellular automaton

## Quick and dirty directory map

`main.py` is the actual project code

`main_old.py` is a previous version of `main.py` that I use for personal reference

`params.json` is a set of parameters used by `main.py`. They range from the size of the cellular automaton grid and population size and age demographics to disease metrics like max and min latency period.

## Current state of the project

Need documentation and some features still need to be added. Visualization now errors out because of using too much memory. Fixing later.

## Errors and hiccups I ran into

1. When I switched to using conda environments, I had to add `"python.autoComplete.extraPaths": ["./source/main"],` to my user's `setting.json` file for my modules to stop showing the `unresolved import` error.
2. After switching to a conda environment, I tried to run the simulation and I got `AttributeError: module 'numpy' has no attribute 'ndarray'` error from my Visualizer module. So I used pip in the conda environment to uninstall numpy and setuptools, as suggested by [mehdiHadji on github](https://github.com/ipython/ipyparallel/issues/349#issuecomment-449402168).

## Notes
