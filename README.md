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

You need to have a showdown server running on localhost (`node pokemon-showdown` in the `Pokemon-Showdown` folder). We recommend modifying it at bit to run things more quickly (try running `sh scripts/update-showdown.sh` ;) - this is actually automatically done during installation if you use our installation scripts).

At this point, we are mainly building a proper OOP environnement before moving on to learning. To launch the current project, run `python3 src/main.py`.

## What is implemented

- Base `PlayerNatework` class. Responsible for managing player network interaction (eg. send and receive messages to the server) with as many utilities as deemed useful
- Base `Player` class. Responsible for common player mecanisms. In particular, it can challenge and receive challenges.
- `RandomRandomBattlePlayer`. A player playing random battles in a random fashion. And it works !
- `Battle` class. Stores information on a battle as it goes on.
- `Pokemon` class. Stores information on pokemons during the battle.

## Next steps

- Connect our classes to existing databases.
- Store fighting data.
- Refactor random moves to use vector output converted to instructions
- `import keras` hehehe
  
Once this is done, we can start thinking about ML :)

## To Do

- Fix the consistency of the ident attribute for Pokemons (e.g. "mewtow", not "p1: Mewtow", nor "p1a: Mewtwo", neither "p1: Mewtwo-Z")
- Manage form transforms in Pokemons

## Acknowledgements

We use [Pokemon Showdown](https://github.com/Zarel/Pokemon-Showdown) and our code is built upon the [showdown-battle-bot project](https://github.com/Synedh/showdown-battle-bot). 
