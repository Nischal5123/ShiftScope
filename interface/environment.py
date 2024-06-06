import numpy as np

class environment:
    def __init__(self):
        self.states = []
        self.actions = []
        self.reward = []
    
    def take_step(self, state):
        self.states.append(state)
        length = len(self.states)
        if(length > 1):
            self.actions.append(self.find_action(self.states[length-1], self.states[length-2]))

    def find_action(self, prev_state, cur_state):
        action = np.abs(prev_state - cur_state)
        return action

    def assign_reward(self, reward):
        self.reward.append(reward)
