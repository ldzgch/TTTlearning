import numpy as np


##
class TTTGame():
    """
        Tic-Tac-Toe implementation
    """
    def __init__(self,fieldsize = (3,3),numinline = 3): #two args!
        
        self.field = np.full(fieldsize,-1,dtype=np.int8) #  set to -1 aka empty
        self.initstate = np.full(fieldsize,-1,dtype=np.int8)
        self.numtowin = numinline # length of line needed to win
        self.ended = False
        self.moves_made = 0

    @staticmethod
    def get_legal(state):
        state = state.flatten()
        res = []
        for i in range(state.shape[0]):
            if state[i] == -1:
                res.append(i)
                
        return res
    
    @staticmethod
    def get_sparse_representation( to_convert ):
        #print(is_conv,to_convert.shape)
        ts = to_convert.shape
        to_convert = to_convert.flatten()
        new_array = np.zeros(ts[0]*ts[1]*3,dtype=np.int8)
    
        for i in range(ts[0]*ts[1]):
            if to_convert[i] == -1:
                new_array[i*3 + 0] = 1
            elif to_convert[i] == 0:
                new_array[i*3 + 1] = 1
            else:
                new_array[i*3 + 2] = 1
        else:
            return new_array
        
    def make_move(self, x, y): # main function used during game to enter moves

        plr = self.moves_made % 2
        if self.field[x,y] == -1:       # some validation of the move to be made
        
            self.field[x,y] = plr
            self.moves_made += 1
            #print('move for player: ',plr)
            
            if self.check_turn(plr,[x,y]): # after every move we check whether that move resulted in a win
                self.endgame(plr)
            elif self.moves_made >= np.prod(self.field.shape):    # check for draw -> board full
                self.endgame( -1 )
            return True # ret true if move was accepted
        
                
        else:
            return False

    def get_state(self):
        return self.field
    
    def check_turn(self,who,pos): # function to check move at pos
        # algorithm is supposed to work with fields of arbitrary size
        # we check star-like in all eight directions
        # we always check one direction and the direct 'counterdirection' together so we get causes like: o | pos | o
        
        foundinlineX = 1         # expects self.field[pos] to be == who
        origin = pos[:]
        while pos[0] != 0:
            pos[0] -= 1
            if self.field[pos[0],pos[1]] == who:
                foundinlineX += 1
            else:
                break
            if foundinlineX == self.numtowin:
                return True
        #print(pos)
        pos = origin[:]
        while pos[0] < self.field.shape[0]-1:
            pos[0] += 1
            if self.field[pos[0],pos[1]] == who:
                foundinlineX += 1
            else:
                break
            if foundinlineX == self.numtowin:
                return True
        #print(pos)
        pos = origin[:]
        foundinlineY = 1
        while pos[1] != 0:
            pos[1] -= 1
            if self.field[pos[0],pos[1]] == who:
                foundinlineY += 1
            else:
                break
            if foundinlineY == self.numtowin:
                return True
        #print(pos)
        pos = origin[:]
        while pos[1] < self.field.shape[1]-1:
            pos[1] += 1
            if self.field[pos[0],pos[1]] == who:
                foundinlineY += 1
            else:
                break
            if foundinlineY == self.numtowin:
                return True
        #print(pos)
        pos = origin[:]
        foundindiagL = 1
        while pos[0] != 0 and pos[1] != 0:
            pos[1] -= 1
            pos[0] -= 1
            if self.field[pos[0],pos[1]] == who:
                foundindiagL += 1
            else:
                break
            if foundindiagL == self.numtowin:
                return True
        #print(pos)
        pos = origin[:]
        while pos[0] < self.field.shape[0]-1 and pos[1] < self.field.shape[1]-1:
            pos[0] += 1
            pos[1] += 1
            if self.field[pos[0],pos[1]] == who:
                foundindiagL += 1
            else:
                break
            if foundindiagL == self.numtowin:
                return True
        #print(pos)
        pos = origin[:]
        foundindiagR = 1
        while pos[0] < self.field.shape[0]-1 and pos[1] != 0:
            pos[1] -= 1
            pos[0] += 1
            if self.field[pos[0],pos[1]] == who:
                foundindiagR += 1
            else:
                break
            if foundindiagR == self.numtowin:
                return True
        #print(pos)
        pos = origin[:]
        while pos[0] != 0 and pos[1] < self.field.shape[1]-1:
            pos[0] -= 1
            pos[1] += 1
            if self.field[pos[0],pos[1]] == who:
                foundindiagR += 1
            else:
                break
            if foundindiagR == self.numtowin:
                return True
        return False
    
    def visualize(self): # primitive func to display our field
        tmp = ''
        for x in range(self.field.shape[0]):
            for y in range(self.field.shape[1]):
                tmp += str(self.field[x,y]) + '   '
            tmp += '\n\n'
        print(tmp)
        return None

    def endgame(self,plr):
        self.ended = True
        self.last_winner = plr
        #print('Player '+ str(plr) + ' won!')


# OLD
##class TTTHelper():              # class to simplify data exchange between AIs and the TTTGame
##    def __init__(self,fieldsize = (3,3), numplayers = 2, numinline = 3):
##        
##        self.game = TTTGame(fieldsize, numplayers, numinline)
##        self.done = False
##        self.whos_next = 0
##        self.initstate = str(np.full(fieldsize,-1,dtype=np.int8))
##        
##    def limits(self):
##        x,y = self.game.field.shape
##        numstates = 0 #calc later
##        numactions = x * y
##        return numactions,numstates
##
##    def move(self,action_indice):
##        shp = self.game.field.shape
##        x,y = action_indice // shp[0], action_indice % shp[1]
##        plr = self.whos_next
##        if not self.game.make_move(plr,x,y):
##            return False,-10        # illegal move gets punished
##        
##        self.whos_next = (self.whos_next + 1) % self.game.nplr
##        
##        field = self.game.get_state()
##        sn = str(field)
##        
##        if self.game.ended:
##            self.done = True
##            if self.game.last_winner == -1:
##                return sn, -1       # ret -1 for draw
##            
##            return sn, 1            # if game ends, give reward 1
##        return sn, 0                # if nothing happens, give 0

##    def arraytoint(self,array):
##        tmp = 0
##        i = 0
##        for val in array.flatten():
##            tmp += val * (10**i)
##            i += 1
##
##        return tmp
##
##    def reset(self):
##        self.game = TTTGame(self.game.field.shape,self.game.nplr,self.game.numtowin)
##        self.done = False
##        self.whos_next = 0
##        return

  
if __name__ == '__main__':
    mygame = TTTGame((3,4))
    while not mygame.game_end:
        mygame.visualize()
        x1,y1 = input('Enter Move for Plr 0; x,y: ').split(' ')
        x2,y2 = input('Enter Move for Plr 1; x,y: ').split(' ')
##        a = time.perf_counter()
        mygame.make_move(0,int(x1),int(y1))
##        b = time.perf_counter()
##        print(b-a)
        mygame.make_move(1,int(x2),int(y2))

    
