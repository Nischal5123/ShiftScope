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
        self.attributes_history = [
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
        return random.choice(self.states)

    def get_valid_actions(self):
        if self.current_state is None:
            return self.states

        valid_actions = []
        for i, value in enumerate(self.current_state):
            if value == 1:
                new_state = list(self.current_state)
                new_state[i] = 0
                valid_actions.append(tuple(new_state))
            else:
                for j, field in enumerate(self.fieldnames):
                    if field != 'none' and self.current_state[j] == 0:
                        new_state = list(self.current_state)
                        new_state[i] = 1
                        new_state[j] = 0
                        valid_actions.append(tuple(new_state))

        return valid_actions

    def step(self, action):
        self.previous_state = self.current_state
        self.current_state = action  # In this environment, action is the next state
        reward = self.calculate_reward()
        return self.current_state, reward

    def calculate_reward_viz_knowledge(self):
        cur_state = self.current_state
        cur_state = self.convert_back_to_state(cur_state)
        cur_state = [field for field in cur_state if field.lower() != 'none']
        viz_knowledge = 0
        return viz_knowledge

    def calculate_reward(self):
        match_count = 0
        weight = 1
        for history in reversed(self.attributes_history):
            per_state_match_count = 0
            for i in range(len(self.current_state)):
                if self.current_state[i] == 1 and history[i] == 1:
                    per_state_match_count += 1
                elif self.current_state[i] == 0 and history[i] == 0:
                    per_state_match_count += 1
                else:
                    per_state_match_count -= 5
            match_count += per_state_match_count * weight
            weight *= 0.9
        match_count /= len(self.attributes_history)
        viz_reward = self.calculate_reward_viz_knowledge()
        return match_count + viz_reward

    def update_q_value(self, state, action, reward, next_state, learning_rate, discount_factor):
        current_q_value = self.get_q_value(state, action)
        max_next_q_value = max([self.get_q_value(next_state, a) for a in self.get_valid_actions()])
        new_q_value = current_q_value + learning_rate * (reward + discount_factor * max_next_q_value - current_q_value)
        self.set_q_value(state, action, new_q_value)

    def get_q_value(self, state, action):
        state = tuple(state)
        action = tuple(action)
        if (state, action) not in self.q_values:
            self.q_values[(state, action)] = 0
        return self.q_values[(state, action)]

    def set_q_value(self, state, action, value):
        state = tuple(state)
        action = tuple(action)
        self.q_values[(state, action)] = value

    def convert_back_to_state(self, state):
        return [self.fieldnames[i] for i in range(len(state)) if state[i] == 1]


fieldnames = sorted(['airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date',
                     'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size',
                     'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a',
                     'speed_ias_in_knots', 'none'])
