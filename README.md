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

At this point, we are mainly building a proper OOP environnement before moving on to learning. To launch the current project, run `python3 src/main.py`. It will launch an agent using a pre-trained model. If you want to train your own agent, use `train_policy.py`.

## What is implemented

### Base player classes

- Base `PlayerNetwork` class. Responsible for managing player network interaction (eg. send and receive messages to the server) with as many utilities as deemed useful
- Base `Player` class. Responsible for common player mecanisms. In particular, it can challenge and receive challenges.
- Base `ModelManager` class. Responsible for managing an agent using a keras neural network.
- Base `ModelManagerTF` class. Responsible for managing an agent using a TF neural network.

### Environment

- `Battle` class. Stores information on a battle as it goes on.
- `Pokemon` class. Stores information on pokemons during the battle.
- `Move` class. Stores information on moves.

**This work is considered as good enough** ; there is a lot of things to be done and extended, but the current focus of the project is on implementing a first working battling AI based on the current environment. In particular, please **do not change the API** or the dict returned by **dic_state**.

### Players

- `RandomRandomBattlePlayer`. A player playing random battles in a random fashion. And it works !
- `PolicyNetwork`. An agent based on deep policy reinforcement learning in a pruned environment. It beats the random agent approximately on 90% of the battles. 
- `FullyConnectedRandomModel`. An agent based on deep policy reinforcement learning in a full environment. It is not functional at the time.

## Acknowledgements

We use [Pokemon Showdown](https://github.com/Zarel/Pokemon-Showdown) and our code is built upon the [showdown-battle-bot project](https://github.com/Synedh/showdown-battle-bot). 
