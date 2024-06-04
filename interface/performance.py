import numpy as np
import json
import pandas as pd
import concurrent.futures
from collections import Counter
from flask import Flask, jsonify
from StateGenerator import StateGenerator
# from utils import run_algorithm
import utils
import pdb

class OnlineLearningSystem:
    def __init__(self, dataset='birdstrikes'):
        self.utils_obj = utils.utils()
        self.response_history = []
        self.state_history = []
        self.momentum_attributes_history = []
        self.greedy_attributes_history = []
        self.random_attributes_history = []
        self.ql_attributes_history = []
        self.rl_attributes_history = []
        self.last_users_attributes_history = []
        self.actor_critic_action_history = []
        self.hotspot_attributes_history = []

        #performance data
        self.master_current_user_attributes = None
        self.current_user_attributes = []

        ######
        self.interaction_map = {}
        if dataset == 'birdstrikes':
            self.dataset = dataset
            self.fieldnames = ['airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date',
                      'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size',
                      'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a',
                      'speed_ias_in_knots']

        ### these four are for storing the data needed for performance view ########################################
        self.all_algorithms_distribution_map = {}
        self.user_distribution_map = {}
        self.response_algorithm_predictions = {}
        self.response_accuracy = {}
        ############################################################################################################

    #if algorithm's future is the user's current choice, then it is a hit
    def set_performance_data(self, algorithms=['Momentum', 'Random', 'Greedy']):
        if len(self.current_user_attributes) > 0: #technically this should be the case always
            self.response_algorithm_predictions['RL'] = self.rl_attributes_history
            self.response_algorithm_predictions['Momentum'] = self.momentum_attributes_history
            self.response_algorithm_predictions['Hotspot'] = self.hotspot_attributes_history

            
        
 
    def read_json_file(self, algorithms=['Momentum', 'Random', 'Greedy']):
        # Prepare response data
        response_data = {
            "distribution_map": self.user_distribution_map,
            "baselines_distribution_maps": self.all_algorithms_distribution_map,
            # "algorithm_predictions": self.response_algorithm_predictions
        }
        # pdb.set_trace()
        # Convert self.current_user_attributes to a list if it's a NumPy array
        if isinstance(self.current_user_attributes, np.ndarray):
            response_user = self.current_user_attributes.tolist()
        else:
            response_user = self.current_user_attributes

        # Construct final response
        final_response = {
            'distribution_response': response_data,
            # 'accuracy_response': self.response_accuracy,
            'algorithm_predictions': self.response_algorithm_predictions,
            'user_selections': response_user,
            'recTimetoInteractionTime': self.interaction_map,
            'full_history': self.last_users_attributes_history[1:],
        }
        # pdb.set_trace()
        # Return final response as JSON
        print('Performance data retrieved successfully...')
        return jsonify(final_response)

    def load_json(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def remove_irrelevant_recommendations(self, interested_attributes, recommendations, max_constrained=True):

        chart_recom = []
        chart_all = []
        for chart_key, _ in recommendations.items():
            chart = recommendations[chart_key]
            chart_all.append(chart)
            # encodings = json.loads(chart).get('encoding', {})
            # match = 0

        return chart_all
    
    def get_distribution_of_states(self, data, algo, dataset='birdstrikes'):

        distribution = Counter({key: 0 for key in self.fieldnames})
        if algo != 'algo':
            for state_list in data['State']:
                for state in state_list:
                    for attribute_set in state:
                        if attribute_set.lower() in distribution:
                            distribution[attribute_set.lower()] += 1
        else:
            for state_list in data['State']:
                for state in state_list:
                    if state.lower() in distribution:
                        distribution[state.lower()] += 1

        total = sum(distribution.values()) + 0.000000000000001
        distribution = {key: count / total for key, count in distribution.items()}
        return distribution
    
    def extend_state(self, history):
        history.extend(['none'] * (3 - len(history)))
        return history


    def onlinelearning(self, algorithms_to_run=['Momentum', 'Random', 'Greedy', 'Qlearning', 'ActorCritic'], specified_algorithm='ActorCritic', specified_baseline='Momentum', bookmarked_charts=[], dataset='birdstrikes'):
        # current_interactions = []
        # pdb.set_trace()
        last_history = self.last_users_attributes_history.copy()
        current_history = self.state_history
        for i in range(len(current_history)):
            current_history[i].extend(['none'] * (3 - len(current_history[i])))

        if len(last_history) > 0:
            new_interactions = [attr for attr in current_history[len(last_history):]]
        else:
            new_interactions = []

        self.current_user_attributes.extend(new_interactions)



        #get the hit rate and other performance data ################################################################
        if len(self.rl_attributes_history) > 0:    #before new predictions are made last prection is mapped to new interactions
            # Map the user's position of interaction in the new attributesHistory to the corresponding predictions
            # Determine the indices of the current_user_attributes in attributesHistory
            interaction_indices = list(range(len(last_history), len(current_history)))
            interaction_time_id = len(self.rl_attributes_history)-1
            self.interaction_map[interaction_time_id] = interaction_indices
            self.set_performance_data()
        ############################################################################################################

        #update the last user's attributes history to the current one
        self.last_users_attributes_history = current_history.copy()

        # generator = StateGenerator(dataset)
        generator = None
        df = pd.DataFrame({'State': current_history})
        distribution_map = self.get_distribution_of_states(df, 'algo')
        # pdb.set_trace()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.utils_obj.run_algorithm, algorithm, current_history, generator, dataset): algorithm for algorithm in algorithms_to_run}
            results = {futures[future]: future.result() for future in concurrent.futures.as_completed(futures)}

        # next_state_rl = self.extend_state(results['Qlearning'])
        next_state_momentum = self.extend_state(results['Momentum'])
        next_state_hotspot = self.extend_state(results['Hotspot'])
        next_state_ac = self.extend_state(results['ActorCritic'])


        ############# get the next state based on the specified algorithm and baseline ############################
        next_state_return = results[specified_algorithm]
        next_state_baseline_return = results[specified_baseline]
        print(specified_algorithm, specified_baseline)

        ############################################################################################################

        ####### add new predictions to the history ################################################################

        self.momentum_attributes_history.append(next_state_momentum)
        self.hotspot_attributes_history.append(next_state_hotspot)
        self.actor_critic_action_history.append(next_state_ac)
        self.rl_attributes_history.append(next_state_ac)
        # self.ql_attributes_history.append(next_state_qlearn)
        # self.random_attributes_history.append(next_state_random)

        ############################################################################################################


        df_momentum = pd.DataFrame({'State': self.momentum_attributes_history})
        distribution_map_momentum = self.get_distribution_of_states(df_momentum, 'Momentum')
        df_hotspot = pd.DataFrame({'State': self.hotspot_attributes_history})
        distribution_map_hotspot = self.get_distribution_of_states(df_hotspot, 'Hotspot')
        df_ac = pd.DataFrame(({'State': self.actor_critic_action_history}))
        distribution_map_ac = self.get_distribution_of_states(df_ac, 'ActorCritic')


        distribution_map_rl = distribution_map_ac
        # distribution_map_rl = self.get_distribution_of_states(df_rl, 'ActorCritic')

        # pdb.set_trace()
        all_algorithms_distribution_map = {
            'Momentum': distribution_map_momentum,
            'Hotspot': distribution_map_hotspot,
            'Actor_Critic': distribution_map_ac,
            'RL': distribution_map_rl
        }

         # Store these for everytime the performance view is clicked even if there is no new data need to return this
        self.all_algorithms_distribution_map= all_algorithms_distribution_map
        self.user_distribution_map = distribution_map

        #baseline next state: something other than specified algorithm
        # next_state_baseline = self.extend_state(results['Momentum'])

        return next_state_return, distribution_map, all_algorithms_distribution_map, next_state_baseline_return


    def set_performance_data(self):
        if len(self.current_user_attributes) > 0: #technically this should be the case always
            self.response_algorithm_predictions['RL'] = self.rl_attributes_history.copy()
            self.response_algorithm_predictions['Momentum'] = self.momentum_attributes_history.copy()
            self.response_algorithm_predictions['Hotspot'] = self.hotspot_attributes_history.copy()


    #Updating the Actor-Critic Model based on user's feedback
    def update_models(self):
        Prev_recommended_attributes = self.actor_critic_action_history[-1]
        cur_attributes = self.response_history[-1]

        #Generating reward: Cur_attributes contains the attributes in users clicked recommendations
        #so giving a positive reward to this particular set of attributes
        
        #S = the state for which we generate recommendations
        # A = set of possible recommendations (3) which will be taken by the agent
        #S' = next state (here cur_attribute which was clicked by the recommender)
        # R = reward calculated based on what the user clicked on 

        data = []
        S = self.extend_state(self.state_history[-1])
        S_prime = self.extend_state(cur_attributes)
        for attr_set in Prev_recommended_attributes: #(prev_recommended attributes are each an action)
            if sorted(attr_set) == sorted(cur_attributes):
                total_r = 10
            else:
                total_r = 0

            # total_r = 0
            for attr in attr_set:
                if attr in cur_attributes:
                    total_r += 5

            A = self.extend_state(attr_set)
            R = total_r

            data.append((S, A, R, S_prime, False))

        
        # self.state_history.append(S_prime)
        # pdb.set_trace()

        #Updating the Actor Critic model
        self.utils_obj.ac_model.update_reward(data)

        ########updating the momentum model########
        A = self.extend_state(cur_attributes)
        self.utils_obj.m.update_prob(S, A)

    def save_histories(self, path):
        np.save(path + 'momentum_attributes_history.npy', self.momentum_attributes_history)
        np.save(path + 'hotspot_attributes_history.npy', self.hotspot_attributes_history)
        np.save(path + 'random_attributes_history.npy', self.random_attributes_history)
        np.save(path + 'rl_attributes_history.npy', self.rl_attributes_history)
        np.save(path + 'user_attributes_history.npy', self.current_user_attributes)
        np.save(path + 'actor_critic_attributes_history.npy', self.actor_critic_action_history)
        np.save(path + 'ql_attributes_history.npy', self.ql_attributes_history)

# Assuming other necessary functions like StateGenerator etc. are implemented elsewhere

if __name__ == "__main__":
    print("Starting the Online Learning System")
