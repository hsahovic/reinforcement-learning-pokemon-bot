from environment.battle import Battle
from environment.pokemon import empty_pokemon, Pokemon
from environment.move import empty_move, Move
from players.base_classes.player import Player

from pprint import pprint
from random import choice

# import tensorflow
import keras
from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.models import model_from_json
from keras import activations

import matplotlib.pyplot as plt
import numpy as np

class MLRandomBattlePlayer(Player):
    def __init__(
        self,
        username: str,
        password: str,
        mode: str = "wait",
        *,
        authentification_address=None,
        avatar: int = None,
        log_messages_in_console: bool = False,
        max_concurrent_battles: int = 5,
        server_address: str,
        target_battles: int = 5,
        to_target: str = None,
    ) -> None:
        super(MLRandomBattlePlayer, self).__init__(
            authentification_address=authentification_address,
            avatar=avatar,
            format="gen7randombattle",
            log_messages_in_console=log_messages_in_console,
            max_concurrent_battles=max_concurrent_battles,
            mode=mode,
            password=password,
            server_address=server_address,
            target_battles=target_battles,
            to_target=to_target,
            username=username,
        )

        # NN initialization
        self.input_size = 4*2 + 7 + 5*7 + 7 # Moves + current pokemon 
                                            # + Other pokemons in hand
                                            # + 1 Opponent pokemon 
        self.output_size = 4 + 5 # Moves + Switches
        # Model
        self.model = Sequential()
        self.model.add(Dense(self.input_size, input_dim=self.input_size, activation='relu', kernel_initializer='uniform'))
        self.model.add(Dense(33, activation='relu', kernel_initializer='uniform'))
        self.model.add(Dense(self.output_size, activation='softmax', kernel_initializer='uniform'))
        # Parameters
        self.model.compile(
            loss=keras.losses.binary_crossentropy,
            optimizer=keras.optimizers.Adagrad(),
            metrics=['categorical_accuracy']
        )
        self.model.summary()
        self.batch_size = 32
        self.epochs = 20

    def battle_to_features(self, battle: Battle):
        # First simple model
            # Pokemons: stats (atk, def, spa, spd, spe), current_hp, max_hp 
            # Moves: base_power, accuracy
        # Input:
            # 4 moves
            # current pokemon
            # 5 remaining pokemons
            # opponent active pokemon

        empty_move_feature = np.zeros(2)
        empty_pokemon_feature = np.zeros(7)
        features = np.array([])

        for move in battle.available_moves_object:
            features = np.concatenate((features, self.move_to_feature(move)))

        for _ in range(4 - len(battle.available_moves_object)):
            features = np.concatenate((features, empty_move_feature))

        features = np.concatenate((features, self.pokemon_to_feature(battle.active_pokemon)))
        
        for pokemon in battle.available_switches_object:
            features = np.concatenate((features, self.pokemon_to_feature(pokemon)))

        print(battle.available_switches_object)
        
        for _ in range(5 - len(battle.available_switches)):
            features = np.concatenate((features, empty_pokemon_feature))
        
        features = np.concatenate((features, self.pokemon_to_feature(battle.opp_active_pokemon)))

        # state = battle.dic_state
        # print(battle._player_team)
        # print(battle._opponent_team)
        
        return features.reshape((1,-1))

    def fit(self, X_train, Y_train, batch_size=32, epochs=10, display=False):
        self.batch_size = batch_size
        self.epochs = epochs
        # Train
        history = self.model.fit(X_train, Y_train,
                                batch_size=self.batch_size,
                                epochs=self.epochs,
                                verbose=1,
                                validation_split=.1)
        # Graph Layout
        if display:
            plt.figure(figsize=(7, 5))
            plt.plot(history.epoch, history.history['acc'], lw=3, label='Training')
            plt.plot(history.epoch, history.history['val_acc'], lw=3, label='Testing')
            plt.legend(fontsize=14)
            plt.title('Accuracy of softmax regression', fontsize=16)
            plt.xlabel('Epoch', fontsize=14)
            plt.ylabel('Accuracy', fontsize=14)
            plt.tight_layout()
            plt.show()

            # score = self.model.evaluate(x_test, y_test, verbose=0)
            # print('Test loss:', score[0])
            # print('Test accuracy:', score[1])

    def move_to_feature(self, move: Move):
        return np.array([
            move.base_power,
            move.accuracy
        ])

    def pokemon_to_feature(self, pokemon: Pokemon):
        if pokemon == None:
            return np.zeros(7)

        return np.array([
            pokemon.stats["atk"], 
            pokemon.stats["def"], 
            pokemon.stats["spa"], 
            pokemon.stats["spd"], 
            pokemon.stats["spe"],
            pokemon.current_hp,
            pokemon.max_hp
        ])

    def predict(self, battle: Battle):
        X_test = self.battle_to_features(battle)
        Y_pred = self.model.predict(X_test)
        idx = np.argsort(Y_pred[0])[::-1]
        for i in idx:
            if i < len(battle.available_moves): # 4 first neurons for moves
                return f"/choose move {battle.available_moves[i][0]}"
            if 3 < i and i - 4 < len(battle.available_switches): # Neurons 4 to 8 for switches
                return f"/choose switch {battle.available_switches[i - 4][0]}"
        print("#### WARNING PREDICT")
        return None

    def reset_weights(self):
        session = K.get_session()
        for layer in self.model.layers: 
            if hasattr(layer, 'kernel_initializer'):
                layer.kernel.initializer.run(session=session)

    def save_model(self, title="dense_model"):
        model_json = self.model.to_json()
        with open(title + ".json", "w") as json_file:
            json_file.write(model_json)
        self.model.save_weights(title + ".h5")

    def upload_model(self, source="dense_model"):
        json_file = open(source + '.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        self.model.load_weights(source + ".h5")

        
    async def select_move(self, battle: Battle, *, trapped: bool = False):
        choices = [f"/choose switch {i}" for i, ident in battle.available_switches] + [
            f"/choose move {i}" for i, move in battle.available_moves
        ]
        turn = battle.turn_sent
        if choices:
            to_send = self.predict(battle)
            if "move" in to_send:
                if battle.can_z_move and battle.can_z_move[int(to_send[-1]) - 1]:
                    to_send += " zmove"
                if battle.can_mega_evolve:
                    to_send += " mega"
            await self.send_message(
                message=to_send, message_2=str(turn), room=battle.battle_tag
            )