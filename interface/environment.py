import numpy as np
import csv

class environment:
    def __init__(self):
        self.states = []
        self.actions = []
        self.reward = []

    def take_step(self, state):
        self.states.append(state)
        length = len(self.states)
        if (length > 1):
            self.actions.append(self.find_action(self.states[length - 1], self.states[length - 2]))

    def find_action(self, prev_state, cur_state):
        action = np.abs(prev_state - cur_state)
        return action

    def assign_reward(self, reward):
        self.reward.append(1)


    def save_to_csv(self, filename):
            data = zip(self.states, self.actions, self.rewards)
            with open(filename, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['State', 'Action', 'Reward'])
                csv_writer.writerows(data)

# Example usage
if __name__ == "__main__":
    env = environment()
    # Simulate environment steps and assign states, actions, and rewards
    # ...

    # Save data to CSV when needed
    env.save_to_csv('environment_data.csv')