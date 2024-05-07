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
        # self.valid_actions = ['same', 'modify-1', 'modify-2','modify-3']
        self.attributes_birdstrikes = {'Airport_Name': 1, 'Aircraft_Make_Model': 2, 'Effect_Amount_of_damage': 3, 'Flight_Date': 4, 'Aircraft_Airline_Operator': 5, 'Origin_State': 6, 'When_Phase_of_flight': 7, 'Wildlife_Size': 8, 'Wildlife_Species': 9, 'When_Time_of_day': 10, 'Cost_Other': 11, 'Cost_Repair': 12, 'Cost_Total': 13, 'Speed_IAS_in_knots': 14}


        # Storing the data into main memory. Focus is now only on action and states for a fixed user's particular subtask
        self.mem_states = []
        self.mem_reward = []
        self.mem_action = []
        self.mem_roi = []
        self.prev_state = None

    def get_state(self, cur_attrs):
        state = np.zeros(len(self.attributes_birdstrikes), dtype = np.int32)
        cur_attrs = ast.literal_eval(cur_attrs)
        # pdb.set_trace()
        for attrs in cur_attrs:
            if attrs != 'None':
                state[self.attributes_birdstrikes[attrs]-1] = 1
        
        return state

    def get_action(self, cur_state, prev_state):
        action = np.abs(prev_state - cur_state)
        return action

    def reset(self):
        """
        Reset the variables used for tracking position of the agents.

        :param all: If true, reset all variables.
        :param test: If true, set the current step to threshold value.
        :return: Current state.
        """
        # self.mem_states = []
        # self.mem_action = []
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
                action = self.get_action(cur_state, self.mem_states[-1])
                self.mem_action.append(action)
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

        reward = np.sum((act_arg == 1) & (next_state == 1))
        # Take the step action
        self.take_step_action()

        # Return the predicted next state, current reward, done status, prediction, and top reward
        return next_state, reward, self.done

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
    tasks = ['p1','p2', 'p3', 'p4']
    for dataset in datasets:
        for task in tasks:
            env = environment()
            user_list_name = env.get_user_list(dataset, task)
            # print(user_list_name)
            for u in user_list_name:
                env.process_data(u)
                print(len(env.mem_states), len(env.mem_action))
                env.reset()
                pdb.set_trace() 

                