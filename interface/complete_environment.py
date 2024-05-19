import random
import itertools
import numpy as np
from draco_test import get_draco_recommendations
import json

class RLEnvironment:
    def __init__(self, fieldnames, max_fields_per_state, attributes_history_path):
        self.fieldnames = fieldnames
        self.max_fields_per_state = max_fields_per_state
        self.attributes_original = np.load(attributes_history_path, allow_pickle=True)
        # self.attributes_original = [['when_phase_of_flight', 'flight_date'], ['speed_ias_in_knots']]
        self.attributes_history =[
    tuple([1 if field in attrs else 0 for field in fieldnames])
    for attrs in self.attributes_original
]
        self.states = self.generate_states()
        self.current_state = None
        self.previous_state = None
        self.q_values = {}

    def generate_states(self):
        states = []
        for combination in itertools.combinations(self.fieldnames, 3):
            state = tuple([1 if field in combination else 0 for field in self.fieldnames])
            states.append(state)
            random.shuffle(states)
        return states

    def reset(self):
        self.current_state = None
        self.previous_state = None
        return self.sample_state()

    def sample_state(self):
        # Randomly sample a state
        return random.choice(self.states)

    def step(self, action):
        self.previous_state = self.current_state
        self.current_state = action  # In this environment, action is the next state
        reward = self.calculate_reward()
        return self.current_state, reward

    def calculate_reward_viz_knowledge(self):
        '''This function calculates the reward based on the visualization knowledge.'''
        # Get the current state
        cur_state = self.current_state
        #convert to attributes and remove none
        cur_state = self.convert_back_to_state(cur_state)
        cur_state = [field for field in cur_state if field.lower() != 'none']

        # rec=get_draco_recommendations(cur_state)


        # Call draco to get the visualization knowledge
        #viz_knowledge = draco.get_viz_knowledge(cur_state)
        # json_version=json.loads(rec[next(iter(rec.keys()))])
        viz_knowledge = 0
        return viz_knowledge

    def calculate_reward(self):
        # Initialize match count and weight
        match_count = 0
        weight = 1

        # Iterate over attributes_history in reverse order to give more weight to recent history
        for history in reversed(self.attributes_history):
            per_state_match_count = 0
            for i in range(len(self.current_state)):
                if self.current_state[i] == 1 and history[i] == 1:
                    per_state_match_count += 1
                elif self.current_state[i] == 0 and history[i] == 0:
                    per_state_match_count += 1
                else:
                    per_state_match_count -= 5  # Penalty for mismatch
            # Add per_state_match_count weighted by weight
            match_count += per_state_match_count * weight
            # Decrease weight for the next iteration
            weight *= 0.9  # You can adjust this decay factor as needed

        # Normalize match_count by the number of histories
        match_count /= len(self.attributes_history)

        # Calculate additional reward based on visualization knowledge
        viz_reward = self.calculate_reward_viz_knowledge()

        return match_count + viz_reward



    def update_q_value(self, state, action, reward, next_state, learning_rate, discount_factor):
        # Update Q-value using Q-learning update rule
        current_q_value = self.get_q_value(state, action)
        max_next_q_value = max([self.get_q_value(next_state, a) for a in self.states])
        new_q_value = current_q_value + learning_rate * (reward + discount_factor * max_next_q_value - current_q_value)
        self.set_q_value(state, action, new_q_value)

    def get_q_value(self, state, action):
        # Convert state and action to tuples
        state = tuple(state)
        action = tuple(action)
        # Get Q-value for a state-action pair
        if (state, action) not in self.q_values:
            self.q_values[(state, action)] = 0
        return self.q_values[(state, action)]

    def set_q_value(self, state, action, value):
        # Convert state and action to tuples
        state = tuple(state)
        action = tuple(action)
        # Set Q-value for a state-action pair
        self.q_values[(state, action)] = value

    def convert_back_to_state(self, state):
        return [self.fieldnames[i] for i in range(len(state)) if state[i] == 1]