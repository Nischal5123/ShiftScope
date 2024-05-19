import random
# import matplotlib.pyplot as plt
from tqdm import tqdm
from complete_environment import RLEnvironment


class QLearningAgent:
    def __init__(self, environment, learning_rate=0.1, discount_factor=0.9, initial_epsilon=0.9, min_epsilon=0.01,
                 epsilon_decay_rate=0.80):
        '''
        Initialize Q-learning agent.
        Args:
            environment:
            learning_rate:
            discount_factor:
            initial_epsilon:
            min_epsilon:
            epsilon_decay_rate:
        Decay rate for epsilon. So that early on tries more random actions, later on tries more greedy actions (i.e based on what the user has tried).
        '''

        self.env = environment
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.initial_epsilon = initial_epsilon
        self.epsilon = initial_epsilon
        self.min_epsilon = min_epsilon
        self.epsilon_decay_rate = epsilon_decay_rate

    def choose_action(self, state):
        # Epsilon-greedy action selection
        coin = random.random()
        if coin < self.epsilon:
            return self.env.sample_state()  # Explore: choose a random action which is a random state
        else:
            # Exploit: choose the action with the highest Q-value
            q_values = {a: self.env.get_q_value(state, a) for a in self.env.states}
            return max(q_values, key=q_values.get)

    def train(self, num_episodes):
        episode_rewards = []
        for episode in tqdm(range(num_episodes), desc="Training Progress"):
            state = self.env.reset()
            total_reward = 0
            done = False
            step = 0
            while not done:
                step += 1
                action = self.choose_action(state)
                # print("action", action)
                next_state, reward = self.env.step(action)
                current_q_value = self.env.get_q_value(state, action)
                max_next_q_value = max([self.env.get_q_value(next_state, a) for a in self.env.states])
                new_q_value = current_q_value + self.learning_rate * (
                            reward + self.discount_factor * max_next_q_value - current_q_value)
                self.env.set_q_value(state, action, new_q_value)
                state = next_state
                total_reward += reward
                # Linearly decay epsilon
                #self.epsilon = max(self.min_epsilon, self.initial_epsilon - ((episode / num_episodes) * (self.initial_epsilon - self.min_epsilon)))
                # Print episode number and total reward
                #print(f"Episode {episode + 1}/{num_episodes}, Step {step}, Total Reward: {total_reward}")
                if step > 20:
                    break
            episode_rewards.append(total_reward)
        return episode_rewards

    def inference_predict_next_state(self, inference_state):
        q_values = {a: self.env.get_q_value(inference_state, a) for a in self.env.states}
        best_action = max(q_values, key=q_values.get)
        # Perform the best action to predict the next state
        next_state, _ = self.env.step(best_action)
        # print(f"Next State One-Hot: {next_state}")
        next_state=self.env.convert_back_to_state(next_state)
        return next_state

def convert_to_one_hot(input_attributes, fieldnames):
    one_hot_state = [1 if field in input_attributes else 0 for field in fieldnames]
    return one_hot_state

def Rl_Driver(dataset='birdstrikes', attributes_history_path="attributes_history.npy", current_state=['speed_ias_in_knots', 'aircraft_make_model'], epsilon=0.9):
    if dataset == 'birdstrikes':
        # Define fieldnames, attributes history, and maximum fields per state
        fieldnames = sorted(['airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date',
                      'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size',
                      'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a',
                      'speed_ias_in_knots','none'])

    # # this will come from what the user has selected
   # attributes_history = [['when_phase_of_flight', 'flight_date'], ['speed_ias_in_knots']]
    # # Save attributes history to a numpy file
    # np.save("attributes_history.npy", attributes_history)
    # attributes_history_path = "attributes_history.npy"

    max_fields_per_state = 3

    # Create RL environment
    rl_env = RLEnvironment(fieldnames, max_fields_per_state, attributes_history_path)

    # Create Q-learning agent
    agent = QLearningAgent(rl_env, initial_epsilon=epsilon)

    # Train the agent
    num_episodes = 100
    total_rewards = agent.train(num_episodes)

    # Plot training progress
    # plt.interactive(False)
    # plt.plot(range(1, num_episodes + 1), total_rewards)
    # plt.xlabel('Episode')
    # plt.ylabel('Total Reward')
    # plt.title('Training Progress')
    # plt.show()

    # Inference: Predict the next state
    current_state_encoded = convert_to_one_hot(current_state, fieldnames)
    predicted_next_state = agent.inference_predict_next_state(current_state_encoded)
    # print(f"Inference: Predicted next state: {predicted_next_state}")
    return predicted_next_state


if __name__ == '__main__':
     Rl_Driver(current_state=['when_phase_of_flight', 'aircraft_make_model'])
