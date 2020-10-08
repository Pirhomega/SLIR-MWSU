# SLIR-MWSU

This project seeks to develop a cellular automaton framework for disease simulation in a mixed population.

## Directory tree

```txt
/SLIR-MWSU
├── README.md
├── CHANGELOG.txt
├── .gitignore
├── resources
├────── images
├── source
├── output
```

## State of the project

|   #   | Function / Requirement | % Completed | Latest info |
| :---: | ----------- | ---------------------- | ------- |
|   1   | Simulation runs with SLIR model  | 100% |  Individuals follow model correctly |
|   2   | Simulation runs with SLIS model  | 100% |  Individuals follow model correctly |
|   3   | Individuals can pathfind  | 100% | Used library which pathfinds using A-star or Dijkstra's algorithm |
|   4   | Population environment represented in simulation (obstacles, buildings, etc.)  | 50% | Uses .txt file to add obstacles and space in grid for Individuals to travel over |
|   5   | Population demographics represented in simulation  | 100% | Users can create a dictionary of ages and the ratio of that age within the population |
|   6   | Simulation grid can be set by user | 100% | User can modify grid length and width in parameter file      |
|   7   | Multiple diseases can be simulated in one simulation  | 0% |  Updated parameter file to support multiple diseases     |
|   8   | Infection possibility customizable for each disease  | 0% | Current implementation uses "exposure points." Updated implementation plans to replace with a percent chance |
|   9   | Disease spread prevention measures incoporated (mask wearing, washing hands, quarantining, etc.) | 99% | User can control if an Individual will isolate or wear a mask when they know they're sick |
|   10   | Disease can be accurately represented in simulation | 80% | See change log for details |
|   11   | Project adheres to proper cellular automaton behavior | 100% | Individuals in a cell are only affected by their neighboring cells |
|   12   | Disease spread progress can be visualized | 100% | uses PIL to visualize disease spread throughout entire simulation using .gif |
|   13   | Disease parameters can be modified by the user | 100% | parameter file is modifiable by user |

## Errors and hiccups I ran into

1. When I switched to using conda environments, I had to add `"python.autoComplete.extraPaths": ["./source/main"],` to my user's `setting.json` file for my modules to stop showing the `unresolved import` error.
2. After switching to a conda environment, I tried to run the simulation and I got `AttributeError: module 'numpy' has no attribute 'ndarray'` error from my Visualizer module. So I used pip in the conda environment to uninstall numpy and setuptools, as suggested by [mehdiHadji on github](https://github.com/ipython/ipyparallel/issues/349#issuecomment-449402168).

## Notes
