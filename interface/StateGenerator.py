
import itertools

class StateGenerator:
    def __init__(self, dataset='birdstrikes'):
        if dataset== 'birdstrikes':
            self.fieldnames = ['Airport_Name', 'Aircraft_Make_Model', 'Effect_Amount_of_damage', 'Flight_Date',
              'Aircraft_Airline_Operator', 'Origin_State', 'When_Phase_of_flight', 'Wildlife_Size',
              'Wildlife_Species', 'When_Time_of_day', 'Cost_Other', 'Cost_Repair', 'Cost_Total',
              'Speed_IAS_in_knots', 'None']


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