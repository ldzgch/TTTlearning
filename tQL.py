import numpy as np
import random
from TTTGame import TTTGame

class Q_Learner():                      # class that implements iterative Q-Learning
    def __init__(self,Q_file = None,tttargs=((3,3),3)):
        self.args = tttargs
        self.x = tttargs[0][0]
        self.sz = tttargs[0][0]*tttargs[0][1]
        
        self.Q = {}
        self.random_prob = 0.5
        self.lr = 0.1
        self.decay = 0.9
        self.replay_save = []   # should contain lists: [s, a, r, s']
        self.old_replays = []

        if Q_file:
            self.loadQ(Q_file)

        else:
            self.Q[str(TTTGame(*self.args).initstate)] = np.zeros(self.sz)
            self.Q[''] = np.zeros(self.sz)

    def full_play(self,state):
        try:
            res = self.Q[str(state)]
            besta = -1
            bestr = -1000
            for lglidx in TTTGame.get_legal(state):
                if res[lglidx] > bestr:
                    bestr = res[lglidx]
                    besta = lglidx
            return besta
        except KeyError:
            print("must respond randomly")
            a = np.random.choice(TTTGame.get_legal(state))
        return a

    def play_for_replays(self,nummin): # func that plays games to create training data
        self.old_replays.extend(self.replay_save)
        self.replay_save = []
        
        while len(self.replay_save) < nummin:
            game = TTTGame(*self.args)
            s = game.field
            a = 0
            r = 0
            sn = ''
            first_move = True
            
            while not game.ended:
                
                a = self.query(s)
                s_old = np.copy(s)
                game.make_move(a//self.x,a%self.x)
                
                #s = game.get_state()
##                
##                while not sn:
##                    self.Q[s][a] = -10    # direct 'training' because illegal moves are always wrong, no matter what
##                    a = self.query(s)
##                    sn,r = self.env.move(a)

                if not first_move:
                    self.replay_save[-1][3] = np.copy(s)
                else:
                    first_move = False
                    
                self.replay_save.append([s_old,a,0,''])

            self.replay_save[-2][3] = ''    # delete second last sn position, it's the position of the ended game;
                                            # no actions can be taken there
            if game.last_winner == -1: #draw
                pass
            else:       # last move must have won
                self.replay_save[-1][2] = 1 # positive reward
                self.replay_save[-2][2] = -1 # negative reward
##            
##        for r in self.replay_save:
##            print(r)
        #random.shuffle(self.replay_save)


    def query(self,state):  # returns best move according to self.Q but sometimes takes random desicions to make sure
                            # that trainig data varies, otherwise we would always play the same game since we play against ourselves 
        if str(state) not in self.Q:        # adding new states to save
            self.Q[str(state)] = np.zeros(self.sz)
            
        if random.uniform(0,1) < self.random_prob:
            return np.random.choice( TTTGame.get_legal(state) )

        res = self.Q[str(state)]
        besta = -1
        bestr = -1000
        for lglidx in TTTGame.get_legal(state):
            if res[lglidx] > bestr:
                bestr = res[lglidx]
                besta = lglidx
        return besta

    def choose_from_legal(self,state,r_values): # returns maximum r while also having same index as a legal move
        if type(state) is str:
            return 0
        #besta = None
        bestr = -1000
        for lglidx in TTTGame.get_legal(state):
            if r_values[lglidx] > bestr:
                bestr = r_values[lglidx]
                #besta = lglidx
        return bestr
        
    
    def train(self):        # uses all saved training data to perform updates on self.Q 
        for replay in self.replay_save:
            s,a,r,sn = replay
            self.Q[str(s)][a] = self.Q[str(s)][a] * (1 - self.lr) + self.lr * (r + self.decay * self.choose_from_legal(sn,self.Q[str(sn)]))
            
        #self.replay_save = [] # discard training data

    # saving / loading of Q because we don't want to recreate it every time we run the program
    def saveQ(self,file_where):
        np.save(file_where,self.Q)

    def loadQ(self,file_where):
        self.Q = np.load(file_where)[()] # thanks stackoverflow! 
            
# tests performance of Q against 'random choice' player
# this ensures our program to be atleast functional in it's core
def test(QL,num_games):

    if num_games < 0:
        move_first = False
    else:
        move_first = True
    num_games = abs(num_games)
    
    c = {'wins':0,'losses':0,'draws':0}
    queries = [QL.full_play,lambda state: np.random.choice(TTTGame.get_legal(state))]
    
    for i in range(num_games):
        
        game = TTTGame(*QL.args)
        plr = 0 if move_first else 1

        while not game.ended:
            a = queries[plr](game.get_state())
            game.make_move(a//QL.x,a%QL.x)
            plr = (plr + 1) % 2

        
        if game.last_winner == 0:
            c['wins'] += 1
        elif game.last_winner == 1:
            c['losses'] += 1
        else:
            c['draws'] += 1

    print(c['wins']/num_games * 100,c['losses']/num_games * 100,c['draws']/num_games * 100)


# primitive game between human and Q
def play_against_Q(QL_obj):
    while not QL_obj.env.game.game_end:

        
        
        try: # Q plays
            s = str(QL_obj.env.game.get_state())
            Q_move = np.argmax(QL_obj.Q[s])
            print('QL plans',QL_obj.Q[s].reshape((3,3)))
        except KeyError:
            print('QL plays random')
            Q_move = random.randrange(9)
        
        while not QL_obj.env.game.make_move(0,Q_move // 3,Q_move % 3):
            Q_move = random.randrange(9)
        print('Q_move:', Q_move)
        
        if QL_obj.env.game.game_end:
            break
        
        QL_obj.env.game.visualize() # draw board
        # q move proposals and input
        print(QL_obj.Q[str(QL_obj.env.game.get_state())].reshape((3,3)))
        player_move = int(input('Enter move: '))
        while not QL_obj.env.game.make_move(1,player_move // 3,player_move % 3):
            player_move = int(input('Enter *better* move: '))


       
def main():
    state_fstring = 'tQL_save.npy'
    
    np.set_printoptions(suppress=True)
    QL = Q_Learner()
    while True:
        order = input('Enter task (p,t,tr,q): ')

        if order == 'q':
            break
        elif order == 'p':
            play_against_Q(QL)

        elif order == 't':
            test(QL,int(input('Enter how_many:')))
        elif order == 'tr':
            QL.play_for_replays(int(input('Enter how_many')))
            QL.saveQ(state_fstring)
        
if __name__ == '__main__':
    main()
