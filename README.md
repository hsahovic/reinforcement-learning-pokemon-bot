# inf581-project

The goal of this project is to implement a pokemon battling bot powered by reinforcment learning.

## Installation

### Ubuntu

Run

```
sh scripts/ubuntu-setup.sh
```

### Mac OS

Run

```
sh scripts/macos-setup.sh
```

### Windows

We recommend using a Windows Linux Subsystem. 

## How to run

You need to have a showdown server running on localhost (`node pokemon-showdown` in the `Pokemon-Showdown` folder).

At this point, we are mainly building a proper OOP environnement before moving on to learning. To launch the current project, run `python3 src/main.py`.

If you just want to watch two bots fighting each other, run `python3 src/old_main.py`.

## What is implemented

- Base PlayerNatework class. Responsible for managing player network interaction (eg. send and receive messages to the server) with as many utilities as deemed useful
- Base Player class. Responsible for common player mecanisms. In particular, it can challenge and receive challenges.
- RandomRandomBattlePlayer. A player playing random battles in a random fashion. And it works !

## Next steps

- Proper battle class.
- Proper pokemon and related classes.
- Storing fighting data.
  
Once this is done, we can start thinking about ML :)

## Acknowledgements

We use [Pokemon Showdown](https://github.com/Zarel/Pokemon-Showdown) and our code is built upon the [showdown-battle-bot project](https://github.com/Synedh/showdown-battle-bot). 
