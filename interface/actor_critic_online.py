import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical
# from complete_environment import RLEnvironment
from environment3 import environment
import numpy as np
import torch.optim.lr_scheduler as lr_scheduler
import ast
import pdb

#Hyperparameters
learning_rate = 0.0002
# learning_rate = 1e-5
n_rollout     = 5
warmup_epochs = 10
num_epochs = 201

class ActorCritic(nn.Module):
    def __init__(self):
        super(ActorCritic, self).__init__()
        self.data = []
        
        self.fc1 = nn.Linear(15,32)
        self.fc_pi = nn.Linear(32,470)
        self.fc_v = nn.Linear(32,1)
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        
        nn.init.xavier_uniform_(self.fc1.weight)
        nn.init.zeros_(self.fc1.bias)
        nn.init.xavier_uniform_(self.fc_pi.weight)
        nn.init.zeros_(self.fc_pi.bias)
        nn.init.xavier_uniform_(self.fc_v.weight)
        nn.init.zeros_(self.fc_v.bias)
        
    def pi(self, x, softmax_dim = 0):
        x = F.relu(self.fc1(x))
        x = self.fc_pi(x)
        # prob = F.softmax(x, dim=softmax_dim)
        # Subtract the max logit for numerical stability
        max_logits = torch.max(x, dim=softmax_dim, keepdim=True)[0]
        stabilized_logits = x - max_logits

        # Apply softmax
        prob = F.softmax(stabilized_logits, dim=softmax_dim)
        return prob
    
    def v(self, x):
        x = F.relu(self.fc1(x))
        v = self.fc_v(x)
        return v
    
    def put_data(self, transition):
        self.data.append(transition)
        
    def make_batch(self):
        s_lst, a_lst, r_lst, s_prime_lst, done_lst = [], [], [], [], []
        for transition in self.data:
            s,a,r,s_prime,done = transition
            s_lst.append(s)
            a_lst.append([a])
            r_lst.append([r/10000.0])
            s_prime_lst.append(s_prime)
            done_mask = 0.0 if done else 1.0
            done_lst.append([done_mask])
        
        s_batch, a_batch, r_batch, s_prime_batch, done_batch = torch.tensor(np.array(s_lst), dtype=torch.float), torch.tensor(np.array(a_lst)), \
                                                               torch.tensor(np.array(r_lst), dtype=torch.float), torch.tensor(np.array(s_prime_lst), dtype=torch.float), \
                                                               torch.tensor(np.array(done_lst), dtype=torch.float)

        self.data = []
        return s_batch, a_batch, r_batch, s_prime_batch, done_batch
  
    def train_net(self, gamma):
        s, a, r, s_prime, done = self.make_batch()
        # r = (r - r.mean()) / (r.std() + 1e-9)
        # Check for NaNs in inputs
        if torch.isnan(s).any() or torch.isnan(a).any() or torch.isnan(r).any() or torch.isnan(s_prime).any() or torch.isnan(done).any():
            print("NaNs found in input batches")
            return
        
        td_target = r + gamma * self.v(s_prime) * done
        delta = td_target - self.v(s)
        
        pi = self.pi(s, softmax_dim=1)
        pi_a = pi.gather(1,a)
        loss = -torch.log(pi_a) * delta.detach() + F.smooth_l1_loss(self.v(s), td_target.detach())

        self.optimizer.zero_grad()
        loss.mean().backward()

        # Check for NaNs in gradients before clipping
        for name, param in self.named_parameters():
            if param.grad is not None and torch.isnan(param.grad).any():
                print(f"NaNs found in gradients of {name} before clipping")

        # Clip gradients
        max_norm = 0.5
        torch.nn.utils.clip_grad_norm_(self.parameters(), max_norm)

        # Check for NaNs in gradients after clipping
        for name, param in self.named_parameters():
            if param.grad is not None and torch.isnan(param.grad).any():
                print(f"NaNs found in gradients of {name} after clipping")

        self.optimizer.step()         

class ActorCriticModel:
    def __init__(self, dataset='birdstrikes'):

        self.model = ActorCritic()
        self.model.load_state_dict(torch.load('pretrained_actor_critic.pth'))

        self.fieldnames = None
        if dataset == 'birdstrikes': 
            self.fieldnames = ['airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date',
                            'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size',
                            'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a',
                            'speed_ias_in_knots','none']
            self.attributes_birdstrikes = {'airport_name': 1, 'aircraft_make_model': 2, 'effect_amount_of_damage': 3, 'flight_date': 4, 'aircraft_airline_operator': 5, 'origin_state': 6, 'when_phase_of_flight': 7, 'wildlife_size': 8, 'wildlife_species': 9, 'when_time_of_day': 10, 'cost_other': 11, 'cost_repair': 12, 'cost_total_a': 13, 'speed_ias_in_knots': 14, 'none': 15}

        # self.attribute_history
        self.rl_env = environment()
        #hyper-parameters
        #hyperparameters:
        self.gamma         = 0.9
        self.gamma_decay   = 0.9 
    
    def get_state(self, cur_attrs):
        state = np.zeros(len(self.attributes_birdstrikes), dtype = np.int32)
        # cur_attrs = ast.literal_eval(cur_attrs)
        # pdb.set_trace()
        for attrs in cur_attrs:
            state[self.attributes_birdstrikes[attrs]-1] = 1
        
        return state

    def generate_actions_topk(self, current_state, dataset = 'birdstrikes', k = 1):
        
        state = self.get_state(current_state) #one-hot of current_state
        prob = self.model.pi(torch.from_numpy(state).float())
        topk_prob, topk_actions = torch.topk(prob, k)
        topk_actions = topk_actions.squeeze().tolist()
        ret_action = []
        for a in topk_actions:
            taken_action_one_hot = self.rl_env.inverse_valid_actions[a]
            taken_action = [self.fieldnames[i] for i in range(len(taken_action_one_hot)) if taken_action_one_hot[i] == 1]
            ret_action.append(taken_action)
        
        return ret_action

    def generate_action(self, current_state, dataset = 'birdstrikes'):
            
        state = self.get_state(current_state) #one-hot of current_state
        prob = self.model.pi(torch.from_numpy(state).float())
        m = Categorical(prob)
        a = m.sample().item()
        taken_action_one_hot = self.rl_env.inverse_valid_actions[a]
        taken_action = [self.fieldnames[i] for i in range(len(taken_action_one_hot)) if taken_action_one_hot[i] == 1]
        
        return taken_action

    def update_reward(self, data):
        
        for d in data:
            S, A, R, S_prime, done = d
            s = self.get_state(S)
            # pdb.set_trace()
            a = self.rl_env.valid_actions[tuple(self.get_state(A))]
            r = R
            s_prime = self.get_state(S_prime)
            # print(s, a, r, s_prime, done)
            self.model.put_data((s,a,r,s_prime,done))
        
        self.model.train_net(self.gamma)
        self.gamma *= self.gamma_decay

def lr_lambda(epoch, warmup_epochs=warmup_epochs, num_epochs=num_epochs):
    if epoch < warmup_epochs:
        return float(epoch) / float(max(1, warmup_epochs))
    return max(0.0, float(num_epochs - epoch) / float(max(1, num_epochs - warmup_epochs)))

def main():  
    #hyperparameters:
    gamma         = 0.98
    gamma_decay   = 0.9
    
    model = ActorCritic()
    scheduler = lr_scheduler.LambdaLR(model.optimizer, lr_lambda)
    
    print_interval = 40
    score = 0.0
    
    datasets = ['birdstrikes']
    tasks = ['p4'] #For now let's train the data on open-ended tasks

    for dataset in datasets:
        for task in tasks:
            env = environment()
            user_list_name = env.get_user_list(dataset, task)
            for fname in user_list_name:
                # print(fname)
                env = environment()
                env.process_data(fname)
                for n_epi in range(num_epochs):
                    done = False
                    s = env.reset()
                    while not done:
                        for t in range(n_rollout):
                            prob = model.pi(torch.from_numpy(s).float())
                            if torch.isnan(prob).any():
                                print("NaNs found in probs tensor")
                                print(s)
                            m = Categorical(prob)
                            a = m.sample().item()
                            s_prime, r, done, ground_action = env.step(s, a)
                            model.put_data((s,a,r,s_prime,done))
                            model.put_data((s,ground_action,15,s_prime,done))
                            
                            s = s_prime
                            score += r
                            
                            if done:
                                break                     
                        
                        model.train_net(gamma)
                        scheduler.step()  # Step the scheduler

                    if n_epi%print_interval==0 and n_epi!=0:
                        print("# of episode :{}, avg score : {:.1f}".format(n_epi, score/print_interval))
                        score = 0.0
        torch.save(model.state_dict(), 'pretrained_actor_critic_V2.pth')

    # env.close()

if __name__ == '__main__':
    main() 
    # ac_model = ActorCriticModel('birdstrikes')
    # print(ac_model.generate_action(['aircraft_make_model']))
    # print(ac_model.generate_actions_topk(['aircraft_make_model'], k=5))