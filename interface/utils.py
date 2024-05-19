# Define a function to run each algorithm

import random
import numpy as np
from Q_Learning import Rl_Driver
from Momentum import Momentum
import os
from a3c import a3c_Driver

def run_algorithm(algorithm, attributes_history, generator, dataset):
    if algorithm == 'Qlearning':
        # Save the attribute history to a numpy file
        Rl_attributesHistory = attributes_history.copy()
        # Make all the attributes inside the list to be 3 in size, fill with 'none' if not enough
        for i in range(len(Rl_attributesHistory)):
            if len(Rl_attributesHistory[i]) < 3:
                Rl_attributesHistory[i].extend(['none'] * (3 - len(Rl_attributesHistory[i])))

        # Remove the existing file if it exists
        if os.path.exists("attributes_history.npy"):
            os.remove("attributes_history.npy")

        # Save the new attribute history to a numpy file
        np.save("attributes_history.npy", Rl_attributesHistory)

        next_state_rl = Rl_Driver(dataset=dataset, attributes_history_path="attributes_history.npy", current_state=Rl_attributesHistory[-1])
        return list(filter(lambda x: x.lower() != 'none', next_state_rl))

    elif algorithm == 'Momentum':
        # algo=Momentum()
        # action=algo.MomentumDriver(df_with_actions)
        if len(attributes_history) > 1:
            return list(filter(lambda x: x.lower() != 'none', attributes_history[-2]))
        else:
            return []

    elif algorithm == 'Greedy':
        return list(filter(lambda x: x.lower() != 'none', attributes_history[-1]))

    elif algorithm == 'Random':
        return list(filter(lambda x: x.lower() != 'none', random.choice(generator.generate_independent_next_states())))

    elif algorithm == 'a3c':
        return a3c_Driver(dataset, attributes_history[-1])
