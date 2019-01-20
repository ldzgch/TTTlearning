import tensorflow.keras as tfk
import numpy as np
from copy import copy
from TTTGame import TTTGame
from models import simpleFF

class DQN():
    
    def __init__(self,model_path = None,tttargs=((3,3),3) ):
        self.TTTARGS = tttargs
        self.sz = tttargs[0][0]*tttargs[0][1]
        self.x = tttargs[0][0]    
        if model_path:
            self.net = tfk.models.load_model(model_path)
        else:
            self.net = simpleFF([100,100,self.sz],3*self.sz)

        self.random_prob = 0.6
        self.gamma = 0.9
        self.visual = False
    
    def query(self,state):  # query() now only returns legal moves, if the nn gives an illegal move a higher value,
                            # that one is ignored
                            
        if np.random.random() < self.random_prob:
            return np.random.choice( TTTGame.get_legal(state) )
        else:
            res = self.net.predict(TTTGame.get_sparse_representation(state).reshape((1,-1)))[0]
            
            max_val = -1000
            best_a = None
            for a in TTTGame.get_legal(state):
                if res[a] > max_val:
                    max_val = res[a]
                    best_a = a
                    
            return best_a
        
    def full_play(self,state):
        #print(state)
        res = self.net.predict(TTTGame.get_sparse_representation(state).reshape((1,-1)))[0]
        max_val = -1000
        best_a = None
        for a in TTTGame.get_legal(state):
            if res[a] > max_val:
                max_val = res[a]
                best_a = a
                
        return best_a

    def play_for_replays(self,num_atleast): # func that plays games to create training data

        experiences = []
        
        while len(experiences) < num_atleast:
            if self.visual:
                print('\rNumber of samples:',len(experiences),end='')
                
            game = TTTGame( *self.TTTARGS )
            s = game.get_state() # basically referencing
            first_move = True
            
            while not game.ended:
            
                a = self.query(s)
                s_old = np.copy(s)
                
                game.make_move(a//self.x,a%self.x)
            
                if not first_move:
                    experiences[-1][3] = np.copy(s)
                else:
                    first_move = False
            
                if game.ended:
                    
                    break           
                else:
                    experiences.append( [s_old,a,0,None] )

            if game.last_winner == -1: # fixing rewards and sn states after game ends
                experiences[-1][3] = None
                experiences.append( [s_old,a,0,None] )
        
            else: #else current player must have won
                experiences[-1][2:] = [-1,None] 
                experiences.append( [s_old,a,1,None] )
                
        if self.visual:    
            print('\n')
        return experiences # assuming that tensorflow shuffles them
            
    def max_sn(self,r_values,sn_states): # helper function for self.train
        res = np.zeros(r_values.shape[0])
        for idx in range(r_values.shape[0]):
            sn = sn_states[idx]
            rs = r_values[idx]
            lgl = TTTGame.get_legal(sn)
            if len(lgl) == 0:
                print("halp",sn)
            bestr = -1000
            for moveidx in lgl:
                if rs[moveidx] > bestr:
                    bestr = rs[moveidx]
                else:
                    pass
            res[idx] = bestr
            
        return res
        

    def train( self, experiences ,ret_x_and_y = False):
        numofexp = len(experiences)
        
        s_list = np.array([TTTGame.get_sparse_representation(e[0]) for e in experiences])
        y_list = self.net.predict(s_list)
        
        #y_list2 = np.copy(y_list)
        # get sn values from all exp
        sn = np.array([e[3] for e in experiences if e[3] is not None])
        sn_list = self.max_sn(self.net.predict(np.array(list(map(TTTGame.get_sparse_representation,sn)))),sn) 
        sn_idx = 0
        for i in range(numofexp):
            s,a,r,sn = experiences[i]
            if sn is None:
                sn = 0
            else:
                sn = sn_list[sn_idx]
                sn_idx += 1
            
            target = r + self.gamma * sn
            y_list[i][a] = target # update so that mse loss sets everything to zero and leaves (target - y[i][a])**2
            #print((y_list2[i] - y_list[i]))
            
        if ret_x_and_y: # for external fitting
            return s_list, y_list
        
        self.net.fit(x = s_list, y = y_list, batch_size=2,epochs = 1,shuffle=True,verbose=(1 if self.visual else 0))
        return None

if __name__ == '__main__':
    learner = DQN()
    
    learner.train(learner.play_for_replays(10))
    
