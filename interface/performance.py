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
        self.rl_attributes_history = []
        self.last_users_attributes_history = []
        self.actor_critic_action_history = []
        self.rl_accuracies = []
        self.random_accuracies = []
        self.momentum_accuracies = []
        self.greedy_accuracies = []
        self.master_current_user_attributes = None
        self.current_user_attributes = []
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
        print("Calculating performance data")
        #if there are new interactions
        if self.current_user_attributes: #technically this should be the case always
            rl_history = np.array([sorted(arr) for arr in self.rl_attributes_history])
            random_history = np.array([sorted(arr) for arr in self.random_attributes_history])
            momentum_history = np.array([sorted(arr) for arr in self.momentum_attributes_history])
            current_user_attributes = np.array([sorted(arr) for arr in self.current_user_attributes])

            # -1 because we are looking at if the user interacted with last recommendation
            self.rl_accuracies.append(self.compute_accuracy(rl_history[-1], current_user_attributes))
            self.random_accuracies.append(self.compute_accuracy(random_history[-1], current_user_attributes))
            self.momentum_accuracies.append(self.compute_accuracy(momentum_history[-1], current_user_attributes))

            self.response_accuracy['RL'] = self.rl_accuracies
            self.response_accuracy['Random'] = self.random_accuracies
            self.response_accuracy['Momentum'] = self.momentum_accuracies

            self.response_algorithm_predictions['RL'] = rl_history.tolist()
            self.response_algorithm_predictions['Random'] = random_history.tolist()
            self.response_algorithm_predictions['Momentum'] = momentum_history.tolist()
            print("Performance data calculated", self.response_accuracy)

            # return self.response_accuracy , self.all_algorithms_distribution_map, self.user_distribution_map

    def compute_accuracy(self, rl_prediction, current_history):
        total_matches = 0
        checks = 0
        for prediction in rl_prediction:
            for attributes in current_history:
                checks += 1
                if prediction in attributes:
                    total_matches += 1
        average_matches = total_matches / checks if checks > 0 else 0
        return average_matches

    def read_json_file(self, algorithms=['Momentum', 'Random', 'Greedy']):
        # Prepare response data
        response_data = {
            "distribution_map": self.user_distribution_map,
            "baselines_distribution_maps": self.all_algorithms_distribution_map,
            "algorithm_predictions": self.response_algorithm_predictions
        }

        # Check the type of self.current_user_attributes
        print("Type of self.current_user_attributes:", type(self.current_user_attributes))

        # Convert self.current_user_attributes to a list if it's a NumPy array
        if isinstance(self.current_user_attributes, np.ndarray):
            response_user = self.current_user_attributes.tolist()
        else:
            response_user = self.current_user_attributes

        # Construct final response
        final_response = {
            'distribution_response': response_data,
            'accuracy_response': self.response_accuracy,
            'algorithm_predictions': self.response_algorithm_predictions,
            'user_selections': response_user
        }

        # Return final response as JSON
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
            encodings = json.loads(chart).get('encoding', {})
            match = 0

        return chart_all

    def get_distribution_of_states(self, data, dataset='birdstrikes'):

        distribution = Counter({key: 0 for key in self.fieldnames})

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


    def onlinelearning(self, algorithms_to_run=['Momentum', 'Random', 'Greedy', 'Qlearning', 'ActorCritic'], dataset='birdstrikes'):
        current_interactions = []
        last_history = self.last_users_attributes_history
        attributesHistory = self.state_history
        for i in range(len(attributesHistory)):
            attributesHistory[i].extend(['none'] * (3 - len(attributesHistory[i])))

        if len(last_history) > 2:
            new_interactions = [attr for attr in attributesHistory[len(last_history):]]
        else:
            new_interactions = []

        self.current_user_attributes.extend(new_interactions)
        self.last_users_attributes_history = attributesHistory

        #get the hit rate and other performance data ################################################################
        if len(self.rl_attributes_history) > 1:
            self.set_performance_data()
        ############################################################################################################

        generator = StateGenerator(dataset)
        df = pd.DataFrame({'State': attributesHistory})
        distribution_map = self.get_distribution_of_states(df)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.utils_obj.run_algorithm, algorithm, attributesHistory, generator, dataset): algorithm for algorithm in algorithms_to_run}
            results = {futures[future]: future.result() for future in concurrent.futures.as_completed(futures)}

        next_state_rl = self.extend_state(results['Qlearning'])
        next_state_momentum = self.extend_state(results['Momentum'])
        next_state_greedy = self.extend_state(results['Greedy'])
        next_state_random = self.extend_state(results['Random'])
        next_state_ac = self.extend_state(results['ActorCritic'])
        # next_state_return = results[specified_algorithm]

        ####### add new predictions to the history ################################################################
        self.momentum_attributes_history.append(next_state_momentum)
        self.greedy_attributes_history.append(next_state_greedy)
        self.random_attributes_history.append(next_state_random)
        self.actor_critic_action_history.append(next_state_ac)
        self.rl_attributes_history.append(next_state_rl)
        ############################################################################################################

        df_momentum = pd.DataFrame({'State': self.momentum_attributes_history})
        distribution_map_momentum = self.get_distribution_of_states(df_momentum)

        df_greedy = pd.DataFrame({'State': self.greedy_attributes_history})
        distribution_map_greedy = self.get_distribution_of_states(df_greedy)

        df_random = pd.DataFrame({'State': self.random_attributes_history})
        distribution_map_random = self.get_distribution_of_states(df_random)

        df_rl = pd.DataFrame({'State': self.rl_attributes_history})
        # print(df_rl)
        distribution_map_rl = self.get_distribution_of_states(df_rl)

        df_ac = pd.DataFrame(({'State': [self.actor_critic_action_history[0][-1]]}))
        # print(df_ac)
        # pdb.set_trace()
        distribution_map_ac = self.get_distribution_of_states(df_ac)

        # pdb.set_trace()
        all_algorithms_distribution_map = {
            'Momentum': distribution_map_momentum,
            'Greedy': distribution_map_rl, # lets send this as greedy for now
            'Random': distribution_map_random,
            'Actor_Critic': distribution_map_ac
        }

         # Store these for everytime the performance view is clicked even if there is no new data need to return this
        self.all_algorithms_distribution_map= all_algorithms_distribution_map
        self.user_distribution_map = distribution_map
        ############################################################################################################

        return next_state_ac, distribution_map, all_algorithms_distribution_map

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
            # if sorted(attr_set) == sorted(cur_attributes):
            total_r = 0
            for attr in attr_set:
                if attr in cur_attributes:
                    total_r += 5
            A = self.extend_state(attr_set)
            R = total_r
            data.append((S, A, R, S_prime, False))
        self.state_history.append(S_prime)
        # pdb.set_trace()

        self.utils_obj.ac_model.update_reward(data)
            

    def save_histories(self, path):
        np.save(path + 'momentum_attributes_history.npy', self.momentum_attributes_history)
        np.save(path + 'greedy_attributes_history.npy', self.greedy_attributes_history)
        np.save(path + 'random_attributes_history.npy', self.random_attributes_history)
        np.save(path + 'rl_attributes_history.npy', self.rl_attributes_history)
        np.save(path + 'user_attributes_history.npy', self.current_user_attributes)
        np.save(path + 'actor_critic_attributes_history.npy', self.actor_critic_action_history)

# Assuming other necessary functions like StateGenerator etc. are implemented elsewhere

if __name__ == "__main__":
    print("Starting the Online Learning System")
