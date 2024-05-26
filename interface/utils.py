# Define a function to run each algorithm

from baseline import RandomStrategy
import numpy as np
from Q_Learning import Rl_Driver
# import Q_Learning
from baseline import Momentum
import os
from actor_critic_online import ActorCriticModel

class utils:
    def __init__(self):
        # self.qlearning = Rl_Driver()
        self.ac_model = ActorCriticModel('birdstrikes')
        self.rs = RandomStrategy()
        self.m = Momentum()

    def run_algorithm(self, algorithm, attributes_history, generator, dataset):
        if algorithm == 'Qlearning':
            # Save the attribute history to a numpy file
            Copy_attributesHistory = attributes_history.copy()
            # Make all the attributes inside the list to be 3 in size, fill with 'none' if not enough
            for i in range(len(Copy_attributesHistory)):
                if len(Copy_attributesHistory[i]) < 3:
                    Copy_attributesHistory[i].extend(['none'] * (3 - len(Copy_attributesHistory[i])))

            # Remove the existing file if it exists
            if os.path.exists("attributes_history.npy"):
                os.remove("attributes_history.npy")

            # Save the new attribute history to a numpy file
            np.save("attributes_history.npy", Copy_attributesHistory)

            next_state_rl = Rl_Driver(dataset=dataset, attributes_history_path="attributes_history.npy", current_state=Copy_attributesHistory[-1])
            return next_state_rl

        elif algorithm == 'Momentum':
            current_state= attributes_history[-1]
            return self.m.generate_actions(current_state)
            
        elif algorithm == 'Greedy':
            current_state= attributes_history[-1]
            return self.m.generate_actions(current_state)

        elif algorithm == 'Random':
            return self.rs.generate_actions()
            
        elif algorithm == 'ActorCritic':
            # ac_model = ActorCriticModel('birdstrikes')
            current_state= attributes_history[-1]
            ret = self.ac_model.generate_actions_topk(current_state, k=6)
            return ret
            # return list(filter(lambda x: x.lower() != 'none', next_state_rl))