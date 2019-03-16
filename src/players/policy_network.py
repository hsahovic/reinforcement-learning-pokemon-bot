# -*- coding: utf-8 -*-
"""
Naive fully connected ML Model.

This file is part of the pokemon showdown reinforcement learning bot project,
created by Randy Kotti, Ombeline Lagé and Haris Sahovic as part of their
advanced topics in artifical intelligence course at Ecole Polytechnique.
"""
from environment.utils import data_flattener
from players.base_classes.model_manager_tf import ModelManagerTF

import tensorflow as tf
import numpy as np

H = 195  # Horizon
g = 0.99
alpha = 0.01  # Initial learning rate
beta = 0.0005  # Target learning rate
delta = 0.99  # Learning rate decay
n_episode = 700
sliding_window = 100


class PolicyNetwork(ModelManagerTF):

    MODEL_NAME = "PolicyNetwork"

    def __init__(
        self,
        gamma=g,
        learning_rate=alpha,
        min_learning_rate=beta,
        decay=delta
    ) -> None:
        """
        This defines a fully connected NN going from processed features to a 
        hidden layer of size ???, and then an ouput.
        """
        self.n_features = 4*2 + 8 + 5*8 + 8 # Moves + current pokemon 
                                            # + Other pokemons in hand
                                            # + 1 Opponent pokemon 

        self.gamma = gamma
        self.learning_rate = learning_rate
        self.min_learning_rate = min_learning_rate
        self.decay = decay

        self._build_net()

        self.sess = tf.Session()

        self.sess.run(tf.global_variables_initializer())

    def _build_net(self):

        # Placeholder for inputs (states)
        with tf.name_scope('inputs'):
            self.tf_obs = tf.placeholder(
                tf.float32, [None, self.n_features], name="observations")

        # Hidden layer (l1)
        layer = tf.layers.dense(
            inputs=self.tf_obs,
            units=33,
            activation=tf.nn.tanh,  # tanh activation
            kernel_initializer=tf.random_normal_initializer(
                mean=0, stddev=0.3),
            bias_initializer=tf.constant_initializer(0.1),
            name='fc1'
        )
        # Linear Layer (l2)
        actions = tf.layers.dense(
            inputs=layer,
            units=20,
            activation=None,
            kernel_initializer=tf.random_normal_initializer(
                mean=0, stddev=0.3),
            bias_initializer=tf.constant_initializer(0.1),
            name='fc2'
        )

        # softmax converts to probability
        self.probs = tf.nn.softmax(actions, name='actions')

        # Loss function
        self.tf_action = tf.placeholder(tf.int32, name="action")
        self.tf_advantage = tf.placeholder(tf.float32, name="advantage")
        self.loss = self.tf_advantage * tf.nn.sparse_softmax_cross_entropy_with_logits(
            logits=actions, labels=[self.tf_action])

        # Train step
        self.tf_learning_rate = tf.placeholder(
            tf.float32, name="learning_rate")
        self.train_step = tf.train.AdamOptimizer(
            self.tf_learning_rate).minimize(self.loss)

        # # Value learning
        # # Linear Layer (head)
        # self.value_layer = tf.layers.dense(
        #     inputs=layer,
        #     units=1,
        #     activation=None,
        #     kernel_initializer=tf.random_normal_initializer(
        #         mean=0, stddev=0.3),
        #     use_bias=False,
        #     # bias_initializer=tf.constant_initializer(0.1),
        #     name='value_layer'
        # )
        # self.predicted_value = tf.squeeze(self.value_layer)

        # # Loss function
        # self.tf_target = tf.placeholder(tf.float32, name="target")
        # self.loss_value = tf.losses.mean_squared_error(
        #     labels=self.tf_target,
        #     predictions=self.predicted_value
        #     )

        # # Train step
        # self.train_step_value = tf.train.AdamOptimizer(
        #     self.tf_learning_rate).minimize(self.loss_value)

    def format_x(self, state: dict):
        """
        Here, formatted data is just the flattened dic_state.
        """

        active_moves = state["active"]["moves"]
        active_pokemon = state["active"]
        back = state["back"]
        opponent_active_pokemon = state["opponent_active"]

        x = np.array([])
        for move in active_moves:
            x = np.concatenate((x, self.move_to_feature(move)))
        x = np.concatenate((x, self.pokemon_to_feature(active_pokemon)))
        for pokemon in back:
            x = np.concatenate((x, self.pokemon_to_feature(pokemon)))
        x = np.concatenate((x, self.pokemon_to_feature(opponent_active_pokemon)))

        return x


    def move_to_feature(self, move):
        return np.array([
            move["base_power"],
            move["accuracy"]
        ])

    def pokemon_to_feature(self, pokemon):
        return np.array([
            pokemon["stats"]["atk"], 
            pokemon["stats"]["def"], 
            pokemon["stats"]["spa"], 
            pokemon["stats"]["spd"], 
            pokemon["stats"]["spe"],
            pokemon["current_hp"],
            pokemon["max_hp"],
            pokemon["level"]
        ])


    def predict(self, observation):
        return self.sess.run(self.probs, feed_dict={self.tf_obs: observation})

    # def predict_value(self, observation):
    #     return self.sess.run(self.predicted_value, feed_dict={self.tf_obs: observation[np.newaxis, :]})

    def discounted_return(self, rewards, t_start=0):
        R = 0
        acc_gamma = 1
        for t in range(t_start, len(rewards)):
            R += acc_gamma * rewards[t]
            acc_gamma *= self.gamma
        return R

    def update(self, observation, action, advantage):
        if action == None: ## WHY NONE ACTIONS ????
            return
        self.sess.run(
            self.train_step,
            feed_dict={
                self.tf_obs: observation[np.newaxis, :],
                self.tf_action: action,
                self.tf_advantage: advantage,
                self.tf_learning_rate: self.learning_rate
                }
            )

    # def update_value(self, observation, target):
    #     self.sess.run(
    #         self.train_step_value,
    #         feed_dict={
    #             self.tf_obs: observation[np.newaxis, :],
    #             self.tf_target: target,
    #             self.tf_learning_rate: self.learning_rate
    #             }
    #         )
    
    def train(self, observations, actions, wins):
        for battle_id in observations.keys():
            obs = [self.format_x(el) for el in observations[battle_id]]
            act = actions[battle_id]
            if wins[battle_id]:
                rwd = [100/len(obs)]*len(obs)
            else:
                rwd = [len(obs)/100]*len(obs) 
            self.reinforce(obs, act, rwd)

    def reinforce(self, observations, actions, rewards):
        for t in range(len(actions)):
            R = self.discounted_return(rewards, t_start=t)
            advantage = R
            
            # Value network
            # b = self.predict_value(self.ep_obs[t])
            # advantage = R - b
            # # Update value network
            # self.update_value(self.ep_obs[t], target=R)
            # Exercice 4: Critic

            # Update policy network
            self.update(observations[t], actions[t], advantage)
        # Learning rate decay
        self.learning_rate = max(
            self.decay * self.learning_rate, self.min_learning_rate)
