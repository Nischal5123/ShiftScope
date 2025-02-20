import environment2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical
import plotting
from collections import Counter
import pandas as pd
import json
import os
from collections import defaultdict
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"


eps=1e-35
#Class definition for the Actor-Critic model
class ActorCritic(nn.Module):
    def __init__(self,learning_rate,gamma,tau):
        super(ActorCritic, self).__init__()
        # Class attributes
        self.data = []
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.temperature = tau

        # Neural network architecture
        self.fc1 = nn.Linear(3, 256)
        self.fc_pi = nn.Linear(256, 3)#actor
        self.fc_v = nn.Linear(256, 1)#critic

        # Optimizer
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)

    #The critic network (called self.fc_v in the code) estimates the state value and is trained using the TD error to minimize the difference between the predicted and actual return.
    def pi(self, x, softmax_dim=0):
        """
        Compute the action probabilities using the policy network.

        Args:
            x (torch.Tensor): State tensor.
            softmax_dim (int): Dimension along which to apply the softmax function (default=0).

        Returns:
            prob (torch.Tensor): Tensor with the action probabilities.
        """

        x = F.relu(self.fc1(x))
        x = self.fc_pi(x)
        prob = F.softmax(x, dim=softmax_dim)
        return prob
    #The actor network (called self.fc_pi ) outputs the action probabilities and is trained using the policy gradient method to maximize the expected return.
    def v(self, x):
        """
        Compute the state value using the value network.

        Args:
            x (torch.Tensor): State tensor.

        Returns:
            v (torch.Tensor): Tensor with the estimated state value.
        """

        x = F.relu(self.fc1(x))
        v = self.fc_v(x)
        return v

    def put_data(self, transition):
        """
        Add a transition tuple to the data buffer.

        Args:
            transition (tuple): Tuple with the transition data (s, a, r, s_prime, done).
        """

        self.data.append(transition)

    def make_batch(self):
        """
        Generate a batch of training data from the data buffer.

        Returns:
            s_batch, a_batch, r_batch, s_prime_batch, done_batch (torch.Tensor): Tensors with the
                states, actions, rewards, next states, and done flags for the transitions in the batch.
        """

        s_lst, a_lst, r_lst, s_prime_lst, done_lst = [], [], [], [], []
        for transition in self.data:
            s, a, r, s_prime, done = transition
            s_lst.append(s)
            a_lst.append([a])
            r_lst.append([r])
            s_prime_lst.append(s_prime)
            done_mask = 0.0 if done else 1.0
            done_lst.append([done_mask])

        s_batch, a_batch, r_batch, s_prime_batch, done_batch = torch.tensor(s_lst, dtype=torch.float), \
                                                               torch.tensor(a_lst), \
                                                               torch.tensor(r_lst, dtype=torch.float), \
                                                               torch.tensor(s_prime_lst, dtype=torch.float), \
                                                               torch.tensor(done_lst, dtype=torch.float)
        self.data = []
        return s_batch, a_batch, r_batch, s_prime_batch, done_batch

    def train_net(self):
        """
           Train the Actor-Critic model using a batch of training data.
           """
        s, a, r, s_prime, done = self.make_batch()
        td_target = r + self.gamma * self.v(s_prime) * done
        delta = td_target - self.v(s)

        pi = self.pi(s, softmax_dim=1)
        pi_a = pi.gather(1, a)

        #The first term is the policy loss, which is computed as the negative log probability of the action taken multiplied by the advantage
        # (i.e., the difference between the estimated value and the target value).
        # The second term is the value loss, which is computed as the mean squared error between the estimated value and the target value
        loss = -torch.log(pi_a) * delta.detach() + F.smooth_l1_loss(self.v(s), td_target.detach())

        self.optimizer.zero_grad()
        loss.mean().backward()
        self.optimizer.step()

class Agent():
    def __init__(self, env,learning_rate,gamma,tau,num_rollouts=10):
        self.env = env
        self.learning_rate, self.gamma, self.n_rollout, self.temp=learning_rate,gamma,num_rollouts,tau
        self.state_encoding = {
            "Sensemaking": [1, 0, 0],
            "Foraging": [0, 1, 0],
            "Navigation": [0, 0, 1]
        }

    def convert_idx_state(self, state_idx):
        state = next((key for key, value in self.state_encoding.items() if np.array_equal(value, state_idx)), None)
        return state

    def convert_state_idx(self, state):
        state_idx = self.state_encoding[state]
        return state_idx

    def train(self):
        model = ActorCritic(self.learning_rate, self.gamma,self.temp)
        score = 0.0
        all_predictions = []
        for n_epi in range(50):
            done = False
            s = self.env.reset()
            s=np.array(self.convert_state_idx(s))

            predictions = []
            actions = []
            while not done:
                for t in range(self.n_rollout):
                    prob = model.pi(torch.from_numpy(s).float())
                    m = Categorical(prob)
                    a = m.sample().item()
                    actions.append(a)
                    s_prime, r, done, info,_= self.env.step(self.convert_idx_state(s), a, False)
                    predictions.append(info)
                    ######################

                    s_prime = np.array(self.convert_state_idx(s_prime))

                    ################
                    model.put_data((s, a, r, s_prime, done))

                    s = s_prime

                    score += r

                    if done:
                        break
                #train at the end of the episode: batch will contain all the transitions from the n-steps
                model.train_net()

            # if n_epi % print_interval == 0 and n_epi != 0:
            #   print("# of episode :{}, avg score : {:.1f}, accuracy: {:.1f} , actions{}".format(n_epi, score / print_interval,np.mean(predictions),Counter(actions)))
            score = 0.0
            all_predictions.append(np.mean(predictions))
        print("############ Train Accuracy :{},".format(np.mean(all_predictions)))
        return model, np.mean(predictions)  # return last episodes accuracyas training accuracy




    def test(self,model):

        test_predictions = []
        split_accuracy = defaultdict(list)
        reward_accumulated = [eps]
        reward_possible = [eps]
        for n_epi in range(1):
            done = False
            s = self.env.reset(all=False, test=True)
            s = np.array(self.convert_state_idx(s))
            predictions = []
            actions = []
            score=0
            while not done:
                    prob = model.pi(torch.from_numpy(s).float())
                    m = Categorical(prob)
                    a = m.sample().item()
                    s_prime, r, done, info,true_reward = self.env.step(self.convert_idx_state(s), a, True)
                    predictions.append(info)
                    split_accuracy[self.convert_idx_state(s)].append(info)
                    reward_accumulated.append(r)
                    reward_possible.append(true_reward)
                    ######################

                    s_prime = np.array(self.convert_state_idx(s_prime))
                    ################

                    ################
                    model.put_data((s, a, r, s_prime, done))

                    s = s_prime
                    actions.append(a)

                    score += r

                    if done:
                        break
                    model.train_net()

            print("#Test of episode :{}, avg score : {:.1f}, accuracy: {:.1f}, actions: {}".format(n_epi,
                                                                                                   score,
                                                                                                   np.mean(predictions),
                                                                                                   Counter(actions)))
            test_predictions.append(np.mean(predictions))
            print("############ Test Accuracy :{},".format(np.mean(predictions)))
        return np.mean(test_predictions),split_accuracy,np.mean(reward_accumulated)/np.mean(reward_possible)




def get_threshold(env, user):
    env.process_data(user, 0)
    counts = Counter(env.mem_roi)
    proportions = []
    total_count = len(env.mem_roi)

    for i in range(1, max(counts.keys()) + 1):
        current_count = sum(counts[key] for key in range(1, i + 1))
        proportions.append(current_count / total_count)
    return proportions[:-1]


def run_experiment(user_list, algo, hyperparam_file):
    # Load hyperparameters from JSON file
    with open(hyperparam_file) as f:
        hyperparams = json.load(f)

    # Create result DataFrame with columns for relevant statistics
    result_dataframe = pd.DataFrame(columns=['Algorithm', 'User', 'Threshold', 'LearningRate', 'Discount', 'Temperature', 'Accuracy', 'StateAccuracy', 'Reward'])
    title = algo
    # Extract hyperparameters from JSON file
    learning_rates = hyperparams['learning_rates']
    gammas = hyperparams['gammas']
    temperatures = hyperparams['temperatures']

    # Create plotter and misc objects
    aggregate_plotter =plotting.plotter(None)
    y_accu_all = []

    # Loop over all users
    for u in user_list:
        # Extract user-specific threshold values
        threshold_h = hyperparams['threshold']
        plotter = plotting.plotter(threshold_h)
        y_accu = []
        user_name = get_user_name(u)

        # Loop over all threshold values
        for thres in threshold_h:
            max_accu = -1
            best_learning_rate = 0
            best_gamma = 0
            best_temp = 0
            best_agent = None
            best_model = None

            # Loop over all combinations of hyperparameters
            for learning_rate in learning_rates:
                for gamma in gammas:
                    for temp in temperatures:
                        env = environment2.environment2()
                        env.process_data(u, thres)
                        agent = Agent(env, learning_rate, gamma,temp)
                        model, accuracies = agent.train()

                        # Keep track of best combination of hyperparameters
                        if accuracies > max_accu:
                            max_accu = accuracies
                            best_learning_rate = learning_rate
                            best_gamma = gamma
                            best_agent = agent
                            best_model = model
                            best_temp = temp

            # Print training results
            print("#TRAINING: User: {}, Threshold: {:.1f}, Accuracy: {}, LR: {}, Discount: {}, Temperature: {}".format(user_name, thres, max_accu, best_learning_rate, best_gamma, best_temp))

            # Test the best agent and store results in DataFrame
            test_accuracy, split_accuracy, reward = best_agent.test(best_model)
            accuracy_per_state = format_split_accuracy(split_accuracy)
            y_accu.append(test_accuracy)
            result_dataframe = pd.concat([result_dataframe, pd.DataFrame({
                'User': [user_name],
                'Threshold': [thres],
                'LearningRate': [best_learning_rate],
                'Discount': [best_gamma],
                'Accuracy': [test_accuracy],
                'StateAccuracy': [accuracy_per_state],
                'Algorithm': [title],
                'Reward': [reward]
            })], ignore_index=True)

            # Print testing results
            print("#TESTING: User: {}, Threshold: {:.1f}, Accuracy: {}, LR: {}, Discount: {}, Temperature: {}, Split_Accuracy: {}".format(user_name, thres, test_accuracy, best_learning_rate, best_gamma, best_temp, accuracy_per_state))

        # Plot user-specific results
        plotter.plot_main(y_accu, user_name)
        y_accu_all.append(y_accu)

    # Aggregate all results and plot

    aggregate_plotter.aggregate(y_accu_all, title)

    # Save result DataFrame to CSV file
    result_dataframe.to_csv("Experiments_Folder/{}.csv".format(title), index=False)


def get_user_name(url):
    string = url.split('\\')
    fname = string[len(string) - 1]
    uname = fname.rstrip('.csv')
    return uname

def format_split_accuracy(accuracy_dict):
    main_states=['Foraging', 'Navigation', 'Sensemaking']
    accuracy_per_state=[]
    for state in main_states:
        if accuracy_dict[state]:
            accuracy_per_state.append(np.mean(accuracy_dict[state]))
        else:
            accuracy_per_state.append(None) #no data for that state
    return accuracy_per_state

if __name__ == '__main__':
    env = environment2.environment2()
    user_list_2D = env.user_list_2D
    run_experiment(user_list_2D, 'Actor_Critic', 'sampled-hyperparameters-config.json')