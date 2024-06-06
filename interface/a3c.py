# import gym
# from environment import environment
from environment3 import environment
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical
import torch.multiprocessing as mp
import time
import numpy as np 
import pdb
import os
import random 

# Hyperparameters
n_train_processes = 3
learning_rate = 0.0002
update_interval = 5
gamma = 0.98
max_train_ep = 200
max_test_ep = 300


class ActorCritic(nn.Module):
    def __init__(self):
        super(ActorCritic, self).__init__()
        self.fc1 = nn.Linear(15, 32)
        self.fc_pi = nn.Linear(32, 200)
        self.fc_v = nn.Linear(32, 1)

    def pi(self, x, softmax_dim=0):
        x = F.relu(self.fc1(x))
        x = self.fc_pi(x)
        # Apply softmax to convert logits (x) to probabilities
        prob = F.softmax(x, dim=softmax_dim)
        return prob

    def v(self, x):
        x = F.relu(self.fc1(x))
        v = self.fc_v(x)
        return v


def train(fname, global_model, rank):
    local_model = ActorCritic()
    local_model.load_state_dict(global_model.state_dict())

    optimizer = optim.Adam(global_model.parameters(), lr=learning_rate)

    env = environment()
    # env.load_bookmarks()
    # full_fname = os.path.join(os.getcwd() + '/interactions/Modified', fname)
    # env.make2(full_fname, env.states_bookmarked_idx[fname])
    env.process_data(fname)
    # print(fname)
    for n_epi in range(max_train_ep):
        # print(n_epi)
        done = False
        s = env.reset(False)
        
        print("here {} {}".format(n_epi, len(env.mem_action)))
        while not done:
            s_lst, a_lst, r_lst = [], [], []
            for t in range(update_interval):
                # print("T ", t)
                prob = local_model.pi(torch.from_numpy(s).float())
                #############
                m = Categorical(prob)
                a = m.sample().item()
                ##############
                print(a)
                s_prime, r, done, ground_action = env.step(s, a)
                # print(s, a, s_prime, r, done, ground_action, env.steps)
                s_lst.append(s)
                a_lst.append([a])
                r_lst.append(r)


                s_lst.append(s)
                a_lst.append([20])
                r_lst.append(3)


                s = s_prime
                if done:
                    break
            s_final = torch.tensor(s_prime, dtype=torch.float)
            R = 0.0 if done else local_model.v(s_final).item()
            td_target_lst = []
            for reward in r_lst[::-1]:
                R = gamma * R + reward
                td_target_lst.append([R])
            td_target_lst.reverse()

            s_batch, a_batch, td_target = torch.tensor(np.array(s_lst), dtype=torch.float), torch.tensor(np.array(a_lst)), torch.tensor(np.array(td_target_lst))
            advantage = td_target - local_model.v(s_batch)

            pi = local_model.pi(s_batch, softmax_dim=1)
            pi_a = pi.gather(1, a_batch)
            loss = -torch.log(pi_a) * advantage.detach() + \
                F.smooth_l1_loss(local_model.v(s_batch), td_target.detach())

            optimizer.zero_grad()
            loss.mean().backward()
            for global_param, local_param in zip(global_model.parameters(), local_model.parameters()):
                global_param._grad = local_param.grad
            optimizer.step()
            local_model.load_state_dict(global_model.state_dict())

    # print("training end")
    # env.close()
    # print("Training process {} reached maximum episode.".format(rank))


def test(fname, global_model):
    env = environment()
    # env.load_bookmarks()
    # full_fname = os.path.join(os.getcwd() + '/interactions/Modified', fname)
    # print("Maximum Achievable Reward", env.make2(full_fname, env.states_bookmarked_idx[fname]))
    # env.make2(full_fname, env.states_bookmarked_idx[fname])
    env.process_data(fname)

    score = 0.0
    print_interval = 20
    num_steps = 0 #finding out how many steps you need to find the desired bookmarks

    for n_epi in range(max_test_ep):
        # print(n_epi)
        done = False
        s = env.reset()
        while not done:
            # print(s)
            prob = global_model.pi(torch.from_numpy(s).float())
            a = Categorical(prob).sample().item()
            
            s_prime, r, done, _ = env.step(s, a)

            s = s_prime
            score += r
            num_steps += 1

        if n_epi % print_interval == 0 and n_epi != 0:
            print("# of episode :{}, avg score : {:.1f} avg steps: {:.1f}".format(
                n_epi, score/print_interval, num_steps/print_interval))
            score = 0.0
            num_steps = 0
            time.sleep(10)

    # print("testing end")
    # env.close()

# def a3c_Driver(dataset='birdstrikes', current_attrs=['speed_ias_in_knots', 'aircraft_make_model']):
    
#     model = ActorCritic()
#     model.load_state_dict(torch.load('a3c_model.pth'))
#     print("Current Attribtues: ", current_attrs)
#     ########Convert Current attributes to one-hot encoded states ######
#     if dataset == 'birdstrikes':
#         attributes = {'airport_name': 1, 'aircraft_make_model': 2, 'effect_amount_of_damage': 3, 'flight_date': 4, 'aircraft_airline_operator': 5, 'origin_state': 6, 'when_phase_of_flight': 7, 'wildlife_size': 8, 'wildlife_species': 9, 'when_time_of_day': 10, 'cost_other': 11, 'cost_repair': 12, 'cost_total_a': 13, 'speed_ias_in_knots': 14, 'none': 15}

#     state = np.zeros(len(attributes), dtype = np.int32)
#     for attrs in current_attrs:
#         state[attributes[attrs]-1] = 1
    
#     prob = model.pi(torch.from_numpy(state).float())
#     a = Categorical(prob).sample().item()
    
#     print("Predicted Attrs: ", next_states_rl)
#     return next_states_rl


if __name__ == '__main__':

    # filenames = os.listdir(os.getcwd() + '/interactions/Modified')
    # file_paths = [os.path.join(os.getcwd() + '/interactions/', filename) for filename in filenames]
    # file_paths = [filename for filename in filenames if "logs" in filename]
    
    global_model = ActorCritic()
    global_model.share_memory()
    
    datasets = ['birdstrikes']
    tasks = ['p4'] #For now let's train the data on open-ended tasks

    for dataset in datasets:
        for task in tasks:
            env = environment()
            user_list_name = env.get_user_list(dataset, task)
            # print(user_list_name)
            for fname in user_list_name:
                processes = []
                # print(fname)
                for rank in range(n_train_processes + 1):  # + 1 for test process
                    # print("Here")
                    # if rank == 0:
                    #     p = mp.Process(target=test, args=(fname, global_model,))
                    # else:
                    p = mp.Process(target=train, args=(fname, global_model, rank,))
                    p.start()
                    processes.append(p)
                for p in processes:
                    # print("End")
                    p.join()
                # break
    # torch.save(global_model.state_dict(), 'a3c_model.pth')

    