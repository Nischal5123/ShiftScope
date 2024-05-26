import os
import fnmatch
import pdb
from collections import defaultdict
import glob
import pandas as pd
import numpy as np
import ast
import random
from collections import deque
import ast 
import itertools

class environment:
    def __init__(self):
        """
        Constructor for the environment class.

        Initializes required variables and stores data in memory.
        """
        path = os.getcwd()
        self.user_list_movies_p1 = np.sort(glob.glob(path + "/interactions/data/zeng/processed_interactions_p1/*"))
        # self.user_location_movies_p1 = "data/zeng/processed_interactions_p1/"
        self.user_list_movies_p2 = np.sort(glob.glob(path + "/interactions/data/zeng/processed_interactions_p2/*"))
        # self.user_location_movies_p2 = "data/zeng/processed_interactions_p2/"
        self.user_list_movies_p3 = np.sort(glob.glob(path + "/interactions/data/zeng/processed_interactions_p3/*"))
        # self.user_location_movies_p3 = "data/zeng/processed_interactions_p3/"
        self.user_list_movies_p4 = np.sort(glob.glob(path + "/interactions/data/zeng/processed_interactions_p4/*"))
        # self.user_location_movies_p4 = "data/zeng/processed_interactions_p4/"

        # print(path + "interactions/data/zeng/birdstrikes_processed_interactions_p1/*")

        self.user_list_birdstrikes_p1 = np.sort(glob.glob(path + "/interactions/data/zeng/birdstrikes_processed_interactions_p1/*"))
        # self.user_location_birdstrikes_p1 = "data/zeng/birdstrikes_processed_interactions_p1/"
        self.user_list_birdstrikes_p2 = np.sort(glob.glob(path + "/interactions/data/zeng/birdstrikes_processed_interactions_p2/*"))
        # self.user_location_birdstrikes_p2 = "data/zeng/birdstrikes_processed_interactions_p2/"
        self.user_list_birdstrikes_p3 = np.sort(glob.glob(path + "/interactions/data/zeng/birdstrikes_processed_interactions_p3/*"))
        # self.user_location_birdstrikes_p3 = "data/zeng/birdstrikes_processed_interactions_p3/"
        self.user_list_birdstrikes_p4 = np.sort(glob.glob(path + "/interactions/data/zeng/birdstrikes_processed_interactions_p4/*"))
        # self.user_location_birdstrikes_p4 = "data/zeng/birdstrikes_processed_interactions_p4/"


        # This variable will be used to track the current position of the user agent.
        self.steps = 0
        self.done = False  # Done exploring the current subtask

        # # List of valid actions and states
        self.attributes_birdstrikes = {'Airport_Name': 1, 'Aircraft_Make_Model': 2, 'Effect_Amount_of_damage': 3, 'Flight_Date': 4, 'Aircraft_Airline_Operator': 5, 'Origin_State': 6, 'When_Phase_of_flight': 7, 'Wildlife_Size': 8, 'Wildlife_Species': 9, 'When_Time_of_day': 10, 'Cost_Other': 11, 'Cost_Repair': 12, 'Cost_Total': 13, 'Speed_IAS_in_knots': 14, 'None': 15}
        self.valid_actions = self.generate_actions()
        self.inverse_valid_actions = {v: k for k, v in self.valid_actions.items()}

        # Storing the data into main memory. Focus is now only on action and states for a fixed user's particular subtask
        self.mem_states = []
        self.mem_reward = []
        self.mem_action = []
        self.mem_roi = []
        self.prev_state = None

    def generate_actions(self):
        actions = defaultdict()
        for idx, combination in enumerate(itertools.combinations(self.attributes_birdstrikes.keys(), 3)):
            # print(tuple([1 if field in combination else 0 for field in attributes_birdstrikes.keys()]), idx)
            actions[tuple([1 if field in combination else 0 for field in self.attributes_birdstrikes.keys()])] = idx 

        last_idx = idx + 1
        for idx, attr in enumerate(self.attributes_birdstrikes.keys()):
            z = ['None']
            z.append(attr)
            # print(tuple([1 if field in z else 0 for field in attributes_birdstrikes.keys()]), last_idx)
            actions[tuple([1 if field in z else 0 for field in self.attributes_birdstrikes.keys()])] = last_idx
            last_idx += 1

        return actions

    def get_state(self, cur_attrs):
        state = np.zeros(len(self.attributes_birdstrikes), dtype = np.int32)
        cur_attrs = ast.literal_eval(cur_attrs)
        # pdb.set_trace()
        for attrs in cur_attrs:
            state[self.attributes_birdstrikes[attrs]-1] = 1
        
        return state

    def reset(self, all = False):
        """
        Reset the variables used for tracking position of the agents.

        :param all: If true, reset all variables.
        :param test: If true, set the current step to threshold value.
        :return: Current state.
        """
        if all == True:            
            self.mem_states = []
            self.mem_action = []
            self.done = False
            self.steps = 0
            return None
        
        self.steps = 0
        self.done = False  # Done exploring the current subtask

        return self.mem_states[0]

    def process_data(self, filename):
        """
        Processes the data from the given file and stores it in the object memory.

        Inputs:
        - filename (str): path of the data file.
        Returns: None.
        """

        df = pd.read_csv(filename)
        cnt_inter = 0
        for index, row in df.iterrows():
            cur_state = self.get_state(row['Attribute'])
            if len(self.mem_states) >= 1: 
                # action = self.get_action(cur_state, self.mem_states[-1])
                # self.mem_action.append(action)
                try:    
                    self.mem_action.append(self.valid_actions[tuple(cur_state)])
                except KeyError:
                    print("Cur State", cur_state, row['Attribute'])
                
                # print("State S ", self.mem_states[-1])
                # print("Action A ", self.mem_action[-1])
                # print("State S' ", cur_state)               

            self.mem_states.append(cur_state)

            # reward = row['Reward']
            # self.mem_reward.append(reward)
            
            cnt_inter += 1
      
    def cur_inter(self, steps):
        """
        Returns the current state, reward, and action from the object memory.

        Inputs:
        - steps (int): current step of the episode.

        Returns:
        - (str): current state.
        - (float): current reward.
        - (str): current action.
        """
        # return self.mem_states[steps], self.mem_reward[steps], self.mem_action[steps]
        return self.mem_states[steps], self.mem_action[steps]


    def peek_next_step(self):
        """
        Returns whether the next step exists and its index.

        Inputs: None.

        Returns:
        - (bool): True if the next step does not exist, False otherwise.
        - (int): index of the next step.
        """
        if len(self.mem_action) > self.steps + 1:
            return False, self.steps + 1
        else:
            return True, 0

    def take_step_action(self):
        """
        Takes a step in the episode.

        Returns: None.
        """
        if len(self.mem_action) > self.steps + 1:
            self.steps += 1
        else:
            self.done = True
            self.steps = 0


    def step(self, cur_state, act_arg):
        # Get the current state, reward, and action at the current step
        # _,  cur_action = self.cur_inter(self.steps)

        # Peek at the next step to get the next state, reward, and action
        _, temp_step = self.peek_next_step()
        # print(temp_step, len(self.mem_action))
        next_state, next_action = self.cur_inter(temp_step)
        taken_action = list(self.valid_actions.keys())[act_arg]
        # reward = np.sum((act_arg == 1) & (next_state == 1))
        reward = 0
        # print(next_state)
        # print(taken_action)
        for i in range(len(next_state)):
            if next_state[i] == 1 and taken_action[i] == 1:
                reward += 1
            elif next_state[i] == 0 and taken_action[i] == 0:
                reward += 1
            else:
                reward -= 2  # Penalty for mismatch
        # Take the step action
        self.take_step_action()
        ground_action = self.valid_actions[tuple(next_state)]
        # Return the predicted next state, current reward, done status, prediction, and top reward
        return next_state, reward, self.done, ground_action

    def get_user_list(self,dataset,task):
        if dataset == 'movies':
            if task == 'p1':
                return self.user_list_movies_p1
            elif task == 'p2':
                return self.user_list_movies_p2
            elif task == 'p3':
                return self.user_list_movies_p3
            elif task == 'p4':
                return self.user_list_movies_p4
        elif dataset == 'birdstrikes':
            if task == 'p1':
                return self.user_list_birdstrikes_p1
            elif task == 'p2':
                return self.user_list_birdstrikes_p2
            elif task == 'p3':
                return self.user_list_birdstrikes_p3
            elif task == 'p4':
                return self.user_list_birdstrikes_p4


if __name__ == "__main__":
    datasets = ['birdstrikes']
    # tasks = ['p1','p2', 'p3', 'p4']
    tasks = ['p4']
    
    for dataset in datasets:
        for task in tasks:
            env = environment()
            print(len(env.valid_actions))
            user_list_name = env.get_user_list(dataset, task)
            # print(user_list_name)
            for u in user_list_name:
                env.process_data(u)
                print(len(env.mem_states), len(env.mem_action))
                env.reset(True)
                break
                # pdb.set_trace() 

                