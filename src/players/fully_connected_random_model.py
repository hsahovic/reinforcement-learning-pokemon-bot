# -*- coding: utf-8 -*-
"""
Naive fully connected ML Model.

This file is part of the pokemon showdown reinforcement learning bot project,
created by Randy Kotti, Ombeline Lagé and Haris Sahovic as part of their
advanced topics in artifical intelligence course at Ecole Polytechnique.
"""
from environment.utils import data_flattener
from players.base_classes.model_manager import ModelManager

from keras.models import Sequential
from keras.layers import Dense


class FullyConnectedRandomModel(ModelManager):

    MODEL_NAME = "FullyConnected"

    def __init__(self) -> None:
        """
        This defines a fully connected NN going from raw flattened dic_states to a 
        hidden layer of size 512, and then an ouput.
        """
        self.model = Sequential()

        self.model.add(Dense(512, input_dim=5390, activation="elu"))
        self.model.add(Dense(20, activation="softmax"))

        self.model.compile(
            loss="categorical_crossentropy", optimizer="rmsprop", metrics=["accuracy"]
        )

        print(self.model.summary())

    def format_x(self, state:dict):
        """
        Here, formatted data is just the flattened dic_state.
        """
        return data_flattener(state)
