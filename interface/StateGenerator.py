
import itertools
import numpy as np

class StateGenerator:
    def __init__(self, dataset='birdstrikes'):
        if dataset== 'birdstrikes':
            self.dataset = 'birdstrikes'
            self.fieldnames = ['airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date', 'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size', 'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a', 'speed_ias_in_knots']



    def generate_next_states(self, current_state, action):
        """

        :param current_state:
        :param action:
        :return: all possible next states
        """
        next_states = []
        # Convert current state to lowercase
        all_combinations = [field.lower() for field in self.fieldnames]
        current_state_lower=[field.lower() for field in self.fieldnames]
        # Iterate over all combinations of fields (up to 3 fields)
        for num_fields in range(1, 4):
            for fields_combination in itertools.combinations(all_combinations, num_fields):
                next_state = list(current_state_lower)  # Make a copy of the current state
                # Apply the action to the fields combination
                if action == 'same':
                    return [current_state] # Keep the same fields
                elif action.startswith('modify'):
                    # Modify the specified number of fields
                    modify_count = int(action.split('-')[1])
                    #To be implemented

        return [current_state]

    def generate_independent_next_states(self):
        # Check if already exists
        try:
            filename= self.dataset + '_all_states.npy'
            all_states = np.load(filename, allow_pickle=True)
            return all_states
        except FileNotFoundError:
            all_states = []
            for num_fields in range(1, 4):
                for fields_combination in itertools.combinations(self.fieldnames, num_fields):
                    all_states.append(list(fields_combination))
            # Convert to numpy array of dtype=object
            all_states = np.array(all_states, dtype=object)
            # Save this as numpy array so that it can handle variable-length lists
            save_path = self.dataset + '_all_states.npy'
            np.save(save_path, all_states)
        return all_states


if __name__ == '__main__':
    sg = StateGenerator()
    list=sg.generate_independent_next_states()

