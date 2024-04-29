import environment_vizrec
import numpy as np
from collections import defaultdict
import random
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd


class Momentum:
    """
    Momentum
    """

    def __init__(self):
        """
        Initializes the Momentum object.
        """
        self.bestaction = defaultdict(
            lambda: defaultdict(str)
        )  # Initializes a dictionary with default values
        self.reward = defaultdict(
            lambda: defaultdict(float)
        )  # Initializes a dictionary with default values
        self.states = []  # Defines the possible states of the environment
        self.actions =['same', 'modify-1', 'modify-2','modify-3'] # Defines the possible actions of the agent
        #self.actions = ['same', 'modify']  # Defines the possible actions of the agent
        self.bestaction = defaultdict(lambda: self.take_random_action('',''))
        self.reward = defaultdict(lambda: defaultdict(float))

    def take_random_action(self, state, action):
        """
        Selects a random action different from the current one.

        Args:
        - state (str): the current state of the environment.
        - action (str): the current action taken by the agent.

        Returns:
        - next_action (str): a randomly chosen action different from the current one.
        """
        #action_space = ['same', 'modify-x', 'modify-y', 'modify-z', 'modify-x-y', 'modify-y-z', 'modify-x-z','modify-x-y-z']
        #action_space=['same', 'modify']
        action_space = [f for f in self.actions if f != action]
        next_action = random.choice(action_space)
        return next_action

    def MomentumDriver(self, data):
        threshold= len(data)
        for i in range(threshold-1):
            self.bestaction[str(data['State'][i])] = data['Action'][i]

        try:  # Finding the last action in the current state
            candidate = self.bestaction[str(data['State'][threshold-1])]
        except KeyError:  # Randomly picking an action if the current state is new
            candidate = random.choice(self.actions)

        return candidate