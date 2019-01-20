import pygame
from DQN import DQN
from tQL import Q_Learner
from TTTGame import TTTGame
drw = pygame.draw


pygame.init()
clock = pygame.time.Clock()


class The_Game():
    def __init__(self,TTTARGS):
        ##
        self.SCRN_SZ = X,Y = [800,800]  #[x,y]
        N_GRID_X,N_GRID_Y = TTTARGS[0]
        
        B_l = 50
        B_r = 50
        B_t = 50
        B_b = 50
        
        self.B = [B_l,B_r,B_t,B_b]

        Fx = (X-B_l-B_r)/(N_GRID_X)
        Fy = (Y-B_t-B_b)/(N_GRID_Y)

        self.xy = [N_GRID_X,N_GRID_Y,Fx,Fy]
        BLACK = (0,0,0)
        WHITE = (255,255,255)
        
        self.col = [BLACK,WHITE]

        self.collision_test = [pygame.Rect(B_l + Fx * (i%N_GRID_X),B_t + (i//N_GRID_Y)*Fy,Fx,Fy) for i in range(N_GRID_X*N_GRID_Y)]

        fnt = pygame.font.SysFont('arial',50)
        x_surf = fnt.render('x',False,BLACK)
        o_surf = fnt.render('o',False,BLACK)
        self.surf = [x_surf,o_surf]
        
        self.args = TTTARGS

    def play(self,enemy,first = True):

        b = Backend(enemy,self)
        state = b.new(first)
        
        screen = pygame.display.set_mode(self.SCRN_SZ)

        ok = True
        while ok:
            
            screen.fill(self.col[1])
            self.draw_grid(state,screen)
            pygame.display.flip()

            state,ok = b.step()

        pygame.display.quit()
        pygame.display.init()





    def draw_grid(self,field,screen):
        B_l,B_r,B_t,B_b = self.B
        N_GRID_X,N_GRID_Y,Fx,Fy = self.xy
        
        screen.lock()
        for x in range(0,N_GRID_X+1):
            #print([B_l + x * F_x,B_b])
            drw.line( screen, self.col[0], [B_l + x * Fx,B_t], [B_l + x * Fx,self.SCRN_SZ[1]-B_b],1)
        for y in range(0,N_GRID_Y+1):
            drw.line( screen, self.col[0], [B_l,B_t + y * Fy], [self.SCRN_SZ[0]-B_r,B_t + y * Fy],1)

        screen.unlock()
        for f in zip(field.flatten(),self.collision_test):
            if f[0] == 0:
                screen.blit(self.surf[0],f[1].center)
            if f[0] == 1:
                screen.blit(self.surf[1],f[1].center)
                
    #    screen.unlock()




    def find_pos(self,pos):
        
        i = 0
        while i < len(self.collision_test):
            if self.collision_test[i].collidepoint(pos):
                return i
            i += 1
        return None


    def UI_input(self,state):
        while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return 'quit'
                
                pos = pygame.mouse.get_pos()
                #print(pos)
                if pygame.mouse.get_pressed()[0]:
                    f = self.find_pos(pos)
                    if f in TTTGame.get_legal(state):
                        return f
                clock.tick(10)
                
def control_loop():
    level0 = "enter letter: \nq(quit),\nn(new DQN),\nt(train current network),\np(play against net),\nc(config),\nl(load),\ns(save)\n>>> "
    leveln = "replace old network? j/N "
    levelt = "train for how many samples? enter NUM:"
    leveltE = "not a number"
    levell = "enter file name:"
    levellE = "file not found"
    levels = "enter file name to save to:"
    levelc = "change settings? j/N"
    TTTARGS = ((3,3),3)
#Qd.TTTARGS = tttargs
    d = DQN('DQN3x3final.h5',tttargs=TTTARGS)
    d.visual = False
    c = input(level0)[0]
    while c != 'q':
        if c == 'n':
            c = input(leveln)[0]
            if c == 'j':
                d = DQN(tttargs=TTTARGS)
                d.visual = False
            else:
                pass

        if c == 't':
            c = input(levelt)
            try:
                num = int(c)
                data = d.play_for_replays(num)
                d.train(data)
            except ValueError:
                print(leveltE)
            
        if c == 'p':
            The_Game(TTTARGS).play(d)
        if c == 'l':
            file = input(levell)
            try:
                d = DQN(model_path=file,tttargs=TTTARGS)
            except OSError:
                print(levellE)
            print("done")

        if c == 's':
            file = input(levels)
            d.net.save(file)
        if c == 'c':
            print("\nTTT settings: {}\nDQN settings: {}".format(TTTARGS,d.net.get_config()))
            c = input(levelc)[0]
            if c == 'j':
                T = input("enter new tttargs:")
                tmp = list(map(int,T.split(' ')))
                TTTARGS = ((tmp[0],tmp[1]),tmp[2])
                print("renewing DQN, entered parametres: ",TTTARGS)
                d = DQN(tttargs=TTTARGS)
                d.visual = False
            else:
                pass
        c = input(">>> ")[0]
    print('quit')
    pygame.quit()


class Backend():
    @staticmethod
    def game_helper(__TTTARGS):
        game = TTTGame(*__TTTARGS)
        
        while not game.ended:
            a = yield game.get_state()        
            ok = game.make_move(a//__TTTARGS[0][0],a%__TTTARGS[0][0])
            if not ok:
                print("move given could not be executed!")
                return
        yield game.get_state()
        return
    
    def __init__(self,AI,UI):
        self.ai = AI
        self.ui = UI
        

    def new(self,UI_first=True):
        if UI_first:
            self.q_list = [self.ui.UI_input,self.query_AI]
        else:
            self.q_list = [self.ui.UI_input,self.query_AI][::-1]
            
        self.game = Backend.game_helper(self.ui.args)
        self.state = next(self.game)
        self.player = 0
        return self.state
        
    def step(self):
        a = self.q_list[self.player](self.state)
        if a == 'quit':
            return self.state,False #assuming ui_input quit
        try:
            self.state = self.game.send(a)
        except StopIteration:
            return self.state,False
        except TypeError:
            print(self.ai.net.get_weights())
        
        self.player = (self.player + 1) % 2    
        return self.state,True
    
    def query_AI(self,state):
        if isinstance(self.ai,DQN):
            
            a = self.ai.full_play(state)
        elif isinstance(self.ai,Q_Learner):
            a = self.ai.full_play(state)

        return a
if __name__ == '__main__':
    control_loop()
    #g = The_Game(TTTARGS)
    #g.play(d)
