# Define a function to run each algorithm

from baseline import RandomStrategy
import numpy as np
from Q_Learning import Rl_Driver
# import Q_Learning
from baseline import Momentum
from baseline import Hotspot
import os
# from actor_critic_online import ActorCriticModel
from actor_critic_online_RLHF import ActorCriticModel as ActorCriticModelRLHF

def attribute_similarity(attr1, attr2):

    # Exact match
    if attr1 == attr2:
        return 2.0

    # Synonyms or strong relationships
    synonyms = {
        "cost_total_a": ["cost_other", "cost_repair"],  
        "cost_other": ["cost_total_a", "cost_repair"],
        "cost_repair": ["cost_total_a", "cost_other"],
        "aircraft_make_model": ["aircraft_airline_operator"],  
        "aircraft_airline_operator": ["aircraft_make_model"],
        "flight_date": ["when_time_of_day"],  # Temporal relationship
        "when_time_of_day":["flight_date"],
        "when_phase_of_flight": ["speed_ias_in_knots"],  # Specific speeds for flight phases
        "speed_ias_in_knots":["when_phase_of_flight"],
        "wildlife_size": ["wildlife_species"],  # wildlife
        "wildlife_species": ["wildlife_size"],
    }
    if attr1 in synonyms and attr2 in synonyms[attr1]:
        return 0.8  # Strong similarity

    # Weaker relationships 
    loose_relationships = {
        "airport_name": ["origin_state", "aircraft_airline_operator"],
        "origin_state": ["airport_name"],
        "effect_amount_of_damage": ["aircraft_make_model", "wildlife_size", "speed_ias_in_knots"]
    }
    if attr1 in loose_relationships and attr2 in loose_relationships[attr1]:
        return 0.5  # Moderate similarity

    # No clear relationship
    return 0.0

def sort_by_lexical_similarity(recommended_sets, current_state, attribute_similarity_func=attribute_similarity):

    # Calculate pairwise similarities between all attributes
    all_attributes = [attr for s in recommended_sets for attr in s] + current_state

    # Initialize a similarity matrix (all zeros)
    num_attributes = len(all_attributes)
    attribute_similarities = np.zeros((num_attributes, num_attributes))

    # Fill the similarity matrix using the provided function
    for i in range(num_attributes):
        for j in range(num_attributes):
            attribute_similarities[i, j] = attribute_similarity_func(all_attributes[i], all_attributes[j])

    # Calculate set similarities
    set_similarities = []
    for set_attributes in recommended_sets:
        set_similarity = 0
        for state_attr in current_state:
            for set_attr in set_attributes:
                state_index = all_attributes.index(state_attr)
                set_index = all_attributes.index(set_attr)
                set_similarity += attribute_similarities[state_index, set_index]
        set_similarities.append(set_similarity)

    # Sort sets based on adjusted similarities, break ties using number of matching attributes
    sorted_sets = sorted(zip(recommended_sets, set_similarities), 
                         key=lambda x: (-x[1], -len(set(x[0]) & set(current_state))))

    return [s for s, _ in sorted_sets]

class utils:
    def __init__(self):
        # self.qlearning = Rl_Driver()
        self.ac_model = ActorCriticModelRLHF('birdstrikes')
        self.ac_offline = ActorCriticModelRLHF('birdstrikes')

        self.rs = RandomStrategy()
        self.m = Momentum()
        self.h = Hotspot()

    def run_algorithm(self, algorithm, attributes_history, generator, dataset):
        current_state = attributes_history[-1]
        if algorithm == 'Qlearning':
            # Save the attribute history to a numpy file
            copy_attributesHistory = attributes_history.copy()
            # Make all the attributes inside the list to be 3 in size, fill with 'none' if not enough
            for i in range(len(copy_attributesHistory)):
                if len(copy_attributesHistory[i]) < 3:
                    copy_attributesHistory[i].extend(['none'] * (3 - len(copy_attributesHistory[i])))

            # Remove the existing file if it exists
            if os.path.exists("performance-data/attributes_history.npy"):
                os.remove("performance-data/attributes_history.npy")

            # Save the new attribute history to a numpy file
            np.save("performance-data/attributes_history.npy", copy_attributesHistory)

            next_state_ql = Rl_Driver(dataset=dataset, attributes_history_path="performance-data/attributes_history.npy", current_state=copy_attributesHistory[-1])
            # ret= sort_by_lexical_similarity(next_state_ql, current_state)
            return next_state_ql

        elif algorithm == 'Momentum': #Return Momentum
            ret = self.m.generate_actions(current_state)
            # ret = sort_by_lexical_similarity(ret, current_state)
            return ret

        elif algorithm == 'Greedy': #Hotspot
            ret = self.h.generate_actions(current_state)
            # ret = sort_by_lexical_similarity(ret, current_state)
            return ret

        elif algorithm == 'Random': #AC_OFFline
            ret = self.ac_offline.generate_actions_topk(current_state, k=6)
            # print(ret)
            # ret = sort_by_lexical_similarity(ret, current_state)
            return ret
            
        elif algorithm == 'ActorCritic': #AC_Online
            ret = self.ac_model.generate_actions_topk(current_state, k=6)
            # print(ret)
            # ret = sort_by_lexical_similarity(ret, current_state)
            # print(ret)
            return ret
            # return list(filter(lambda x: x.lower() != 'none', next_state_rl))