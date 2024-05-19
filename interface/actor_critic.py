import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical
from environment3 import environment
import numpy as np

#Hyperparameters
learning_rate = 0.0002
gamma         = 0.98
n_rollout     = 10

class ActorCritic(nn.Module):
    def __init__(self):
        super(ActorCritic, self).__init__()
        self.data = []
        
        self.fc1 = nn.Linear(15,32)
        self.fc_pi = nn.Linear(32,470)
        self.fc_v = nn.Linear(32,1)
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        
    def pi(self, x, softmax_dim = 0):
        x = F.relu(self.fc1(x))
        x = self.fc_pi(x)
        prob = F.softmax(x, dim=softmax_dim)
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
            r_lst.append([r])
            s_prime_lst.append(s_prime)
            done_mask = 0.0 if done else 1.0
            done_lst.append([done_mask])
        
        s_batch, a_batch, r_batch, s_prime_batch, done_batch = torch.tensor(np.array(s_lst), dtype=torch.float), torch.tensor(np.array(a_lst)), \
                                                               torch.tensor(np.array(r_lst), dtype=torch.float), torch.tensor(np.array(s_prime_lst), dtype=torch.float), \
                                                               torch.tensor(np.array(done_lst), dtype=torch.float)

        self.data = []
        return s_batch, a_batch, r_batch, s_prime_batch, done_batch
  
    def train_net(self):
        s, a, r, s_prime, done = self.make_batch()
        td_target = r + gamma * self.v(s_prime) * done
        delta = td_target - self.v(s)
        
        pi = self.pi(s, softmax_dim=1)
        pi_a = pi.gather(1,a)
        loss = -torch.log(pi_a) * delta.detach() + F.smooth_l1_loss(self.v(s), td_target.detach())

        self.optimizer.zero_grad()
        loss.mean().backward()
        self.optimizer.step()         
      
def main():  
    model = ActorCritic()    
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
                fname = '/nfs/hpc/share/sahasa/project/VizGame/interface/interactions/data/zeng/birdstrikes_processed_interactions_p4/pro30_bde_p4_logs.csv'
                env = environment()
                env.process_data(fname)
                for n_epi in range(201):
                    done = False
                    s = env.reset()
                    while not done:
                        for t in range(n_rollout):
                            prob = model.pi(torch.from_numpy(s).float())
                            m = Categorical(prob)
                            a = m.sample().item()
                            s_prime, r, done, ground_action = env.step(s, a)
                            model.put_data((s,a,r,s_prime,done))
                            model.put_data((s,ground_action,20,s_prime,done))
                            
                            s = s_prime
                            score += r
                            
                            if done:
                                break                     
                        
                        model.train_net()
                        
                    if n_epi%print_interval==0 and n_epi!=0:
                        print("# of episode :{}, avg score : {:.1f}".format(n_epi, score/print_interval))
                        score = 0.0
    # env.close()

if __name__ == '__main__':
    main()