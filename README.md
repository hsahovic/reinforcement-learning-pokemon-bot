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

Once everything is up and running, run

```
python3 src/main.py
```

This will load a pre-trained model in an instance of `MLRKBattlePlayer` and make it fight a `RandomRandomBattlePlayer`. If you want to watch the actual battle, you can access your local Pokemon Showdown server at `localhost:8000` and enjoy.

You can also run `src/main_training.py` if you want to retrain the model.

Note that the battle might have difficulties to launch itself (due to network unstabilities). If the execution lasts more than 1 minute, start again. We are still working on fixing this issue, please bear with us.


## What is implemented

### Base player classes

- Base `PlayerNatework` class. Responsible for managing player network interaction (eg. send and receive messages to the server) with as many utilities as deemed useful
- Base `Player` class. Responsible for common player mecanisms. In particular, it can challenge and receive challenges.

### Environment

- `Battle` class. Stores information on a battle as it goes on.
- `Pokemon` class. Stores information on pokemons during the battle.
- `Move` class. Stores information on moves.

**This work is considered as good enough** ; there is a lot of things to be done and extended, but the current focus of the project is on implementing a first working battling AI based on the current environment. In particular, please **do not change the API** or the dict returned by **dic_state** without discussing it extensively beforehand.

This is valid until we create a first working bot. The only exception to this rule regards *battle parsing and callbacks*.

### Players

- `RandomRandomBattlePlayer`. A player playing random battles in a random fashion. And it works !
- `MLRandomBattlePlayer`. Deep RL based on the full state space. Long to train, but can easily be extended. Still a lot of work going on with it !
- `MLRKBattlePlayer` (reduced kernel). Deep RL based on a reduced set of features. It is giving promising results !

## Next steps

- Extend our RL algorithms !
- Improve performance

## Acknowledgements

We use [Pokemon Showdown](https://github.com/Zarel/Pokemon-Showdown) and our code is built upon the [showdown-battle-bot project](https://github.com/Synedh/showdown-battle-bot). 
