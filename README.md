# inf581-project

The goal of this project is to implement a pokemon battling bot powered by reinforcment learning.

## Installation

### Ubuntu

Run

```
sh scripts/ubuntu-setup.sh
```

### Mac OS

There is no setup file right now, but having one derived from `ubuntu-setup.sh` would be nice.

### Windows

We recommend using a Windows Linux Subsystem. 

## How to run

You need to have a showdown server running on localhost (`node pokemon-showdown` in the `Pokemon-Showdown` folder).

You can then run the project with `python3 src/main.py`. This will launch two bots trying to fight each other. 

At this point in the project, the battle will quickly become stuck: we are working on it.

## Acknowledgements

We use [Pokemon Showdown](https://github.com/Zarel/Pokemon-Showdown) and our code is built upon the [showdown-battle-bot project](https://github.com/Synedh/showdown-battle-bot). 
