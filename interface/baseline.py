from environment3 import environment
from collections import defaultdict
import random 
import numpy as np
import pdb 

class RandomStrategy:
    def __init__(self, dataset='birdstrikes'):
        self.rl_env = environment()
        self.action_space_size = len(self.rl_env.valid_actions)
        self.fieldnames = None
        if dataset == 'birdstrikes': 
            self.fieldnames = ['airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date',
                            'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size',
                            'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a',
                            'speed_ias_in_knots','none']
            self.attributes_birdstrikes = {'airport_name': 1, 'aircraft_make_model': 2, 'effect_amount_of_damage': 3, 'flight_date': 4, 'aircraft_airline_operator': 5, 'origin_state': 6, 'when_phase_of_flight': 7, 'wildlife_size': 8, 'wildlife_species': 9, 'when_time_of_day': 10, 'cost_other': 11, 'cost_repair': 12, 'cost_total_a': 13, 'speed_ias_in_knots': 14, 'none': 15}

        
    def generate_actions(self):
        picked_actions = {}
        while len(picked_actions) < 6:
            ch = random.randint(0, self.action_space_size-1)
            picked_actions[ch] = 1
        ret_action = []
        for a in picked_actions.keys():
            taken_action_one_hot = self.rl_env.inverse_valid_actions[a]
            taken_action = [self.fieldnames[i] for i in range(len(taken_action_one_hot)) if taken_action_one_hot[i] == 1]
            ret_action.append(taken_action)
        
        return ret_action        

class Momentum(RandomStrategy):
    def __init__(self, dataset='birdstrikes'):
        super().__init__(dataset)
        self.prob = np.ones((self.action_space_size, self.action_space_size))

        ###normalizing the probability matrix####
        row_sums = self.prob.sum(axis=1, keepdims=True)
        self.prob /= row_sums 
    
    def get_state(self, cur_attrs):
        state = np.zeros(len(self.attributes_birdstrikes), dtype = np.int32)
        # cur_attrs = ast.literal_eval(cur_attrs)
        # pdb.set_trace()
        for attrs in cur_attrs:
            state[self.attributes_birdstrikes[attrs]-1] = 1
        
        return state

    #To emphasize what user did last, we are putting a big probability to that 
    def update_prob(self, state, action):
        s = self.rl_env.valid_actions[tuple(self.get_state(state))] #find the encoded number of the state, first state list -> numpy array -> encoded number 
        a = self.rl_env.valid_actions[tuple(self.get_state(action))]
        # print(s, state, a, action)
        self.prob[s, :] = 0.1 / (self.action_space_size - 1)
        self.prob[s, a] = 0.9    
        
    #pick 'x' actions given the state
    def generate_actions(self, state, k=6):
        # Get probabilities for actions in the given state
        s = self.rl_env.valid_actions[tuple(self.get_state(state))]
        state_probs = self.prob[s]
        # print(state_probs.sum())
        # print(s)
        # Sample 6 actions (without replacement) based on probabilities
        actions = np.random.choice(
            self.action_space_size,   # Number of actions to choose from
            size=k,                    # Choose 6 actions
            replace=False,              # Allow sampling the same action multiple times
            p=state_probs              # Use the probabilities from self.prob
        )
        # print(actions)
        ret_action = []
        for a in actions:
            taken_action_one_hot = self.rl_env.inverse_valid_actions[a]
            taken_action = [self.fieldnames[i] for i in range(len(taken_action_one_hot)) if taken_action_one_hot[i] == 1]
            ret_action.append(taken_action)
        
        return ret_action

class Hotspot(Momentum):
    def __init__(self, dataset='birdstrikes'):
        super().__init__(dataset)
        self.freq = np.ones((self.action_space_size, self.action_space_size))
        self.pretrain()
        
    def pretrain(self):
        datasets = ['birdstrikes']
        tasks = ['p4'] #For now let's train the data on open-ended tasks

        for dataset in datasets:
            for task in tasks:
                env = environment()
                user_list_name = env.get_user_list(dataset, task)
                for fname in user_list_name:
                    # print(fname)
                    env = environment()
                    env.process_data(fname)
                    
                    s = env.reset()
                    done = False
                    while not done:
                        s_prime, r, done, a = env.step(s, 1)
                        s = self.rl_env.valid_actions[tuple(s)]   
                        self.freq[s, a] += 1
                        # pdb.set_trace() 

                        s = s_prime
                        if done:
                            break                     

    
    def update_prob(self, state, action):
        s = self.rl_env.valid_actions[tuple(self.get_state(state))] #find the encoded number of the state, first state list -> numpy array -> encoded number 
        a = self.rl_env.valid_actions[tuple(self.get_state(action))]
        
        self.freq[s, a] += 1
        row_sums = self.freq.sum(axis=1, keepdims=True)
        # print(self.freq[s,a], row_sums)
        self.prob = self.freq / row_sums 
        # print(self.freq[s,a], self.prob[0].sum())
        
    #generating actions should be same as momentum top 6 based on probability

if __name__ == "__main__":
    # r = RandomStrategy()
    # print(r.generate_actions())
    # m = Momentum()
    # m.update_prob(['none', 'effect_amount_of_damage', 'flight_date'], ['none', 'effect_amount_of_damage'])
    # print(m.generate_actions(['none', 'effect_amount_of_damage', 'flight_date']))

    h = Hotspot()
    h.update_prob(['none', 'effect_amount_of_damage', 'flight_date'], ['none', 'effect_amount_of_damage'])
    print(h.generate_actions(['none', 'effect_amount_of_damage', 'flight_date']))