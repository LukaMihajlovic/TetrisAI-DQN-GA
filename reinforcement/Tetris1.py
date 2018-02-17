from Figures1 import Figure
from genetic import Genetic
from state import State
import time
#import pyautogui
import copy
#from selenium import webdriver
import os
#from selenium.webdriver.chrome.options import Options
#import pyautogui
import ctypes
import cv2
import mss
import numpy
from nekimodul import TetrisApp, cell_size, cols, maxfps
import pygame
from DQN import DQNAgent

# Just disables the warning, doesn't enable AVX/FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

EPISODES = 250

class Tetris:

    def __init__(self):

        #reprezentacija stanja
        self.state = []
        for i in range(20):
            self.state.append([])
            for j in range(10):
                self.state[i].append(0)

        self.cleared_lines = 0

        self.game_over = False

    def generate_state_based_on_action_and_figure(self, dict, action, figure):

        keys = dict.keys()

        label = str(figure) + str(action[2])

        current_piece_key = filter(lambda x: label in x, keys)
        current_piece = dict[current_piece_key[0]]

        starting_coordinate = self.coordinate(label)
        width = self.piece_width(label)
        height = len(current_piece)

        highest_available_y = 20
        highest_available = []

        highest_available_x = 0
        if action[1] == 1:
            highest_available_x = starting_coordinate + action[0]
        else:
            highest_available_x = starting_coordinate - action[0]

        #pronalazenje najvise slobodne tacke na sirini figure
        for i in range(highest_available_x-1, highest_available_x-1+width):
            for j in range(20):
                try:
                    if self.state[j][i] == 1:
                        if j <= highest_available_y:
                            highest_available_y = j-1
                        highest_available.append(j-1)
                        break
                    if j == 19:
                        highest_available.append(19)
                except IndexError:
                    for z in self.state:
                        print z
                    print label
                    print action
                    print i
                    print j

        if (all(x==highest_available[0] for x in highest_available)):
            if (highest_available[0] == 19):
                highest_available_y = 19

        if label == "20":
            if highest_available[0] < highest_available[1] and highest_available[0] < highest_available[2]:
                highest_available_y += 1

        elif label == "21":
            if highest_available[1] < highest_available[0]:
                highest_available_y += 1

        elif label == "30":
            if highest_available[2] < highest_available[1] and highest_available[2] < highest_available[0]:
                highest_available_y += 1

        elif label == "31":
            if highest_available[0] < highest_available[1]:
                highest_available_y += 1

        elif label == "53":
            if highest_available[1] < highest_available[0]:
                if (highest_available[0] - highest_available[1]) >= 2:
                    highest_available_y += 2
                else:
                    highest_available_y += 1

        elif label == "52":
            if highest_available[0] < highest_available[1] and highest_available[0] < highest_available[2]:
                highest_available_y += 1

        elif label == "62":
            if highest_available[2] < highest_available[1] and highest_available[2] < highest_available[0]:
                highest_available_y += 1

        elif label == "61":
            if highest_available[0] < highest_available[1]:
                if (highest_available[1] - highest_available[0]) >= 2:
                    highest_available_y += 2
                else:
                    highest_available_y += 1

        elif label == "73":
            if highest_available[1] < highest_available[0]:
                highest_available_y += 1

        elif label == "72":
            if highest_available[0] < highest_available[1] and highest_available[2] < highest_available[1] and highest_available[0] == highest_available[2]:
                highest_available_y += 1

        elif label == "71":
            if highest_available[0] < highest_available[1]:
                highest_available_y += 1

        # postavljanje figure
        ret_val=copy.deepcopy(self.state)
        for i in range(len(current_piece) - 1, -1, -1):
            for j in range(len(current_piece[i]) - 1, -1, -1):
                if current_piece[i][j] == 1:
                    ret_val[highest_available_y - (height - 1) + i][highest_available_x - 1 + j] = 1

        #ciscenje
        highest_available = []
        tetris.check_for_cleared_lines()

        return ret_val



    def coordinate(self, label):
        if label in ["41", "40"]:
            return 4
        else:
            return 5

    def piece_width(self, label):
        if label == "41":
            return 1
        elif label in ["10", "21", "31", "51", "53", "61", "63", "71", "73"]:
            return 2
        elif label in ["20", "30", "50", "52", "60", "62", "70", "72"]:
            return 3
        else:
            return 4

    def check_for_cleared_lines(self):
        broj = 0
        for i in range(20):
            if all(x == 1 for x in self.state[i]):
                self.state.pop(i)
                self.state.insert(0, [0,0,0,0,0,0,0,0,0,0])
                self.cleared_lines += 1


    def generate_states_for_action(self,dict,figure):


        max_rotation=self.max_rotation_of_figure(figure)
        action=[0,0,0]
        ret_val=State()
        for i in range(max_rotation):

            label=str(figure)+str(i)
            starting_coordinate = self.coordinate(label)
            width = self.piece_width(label)
            max_left = starting_coordinate - 1
            current_piece_right_position = starting_coordinate + width - 1
            max_right = 10 - current_piece_right_position

            for j in range(max_left+1):
                action = [j, 0, i]
                ret_val.states.append(self.generate_state_based_on_action_and_figure(dict, action, figure))
                ret_val.actions.append(action)
            for k in range(1,max_right+1):
                action = [k, 1, i]
                ret_val.states.append(self.generate_state_based_on_action_and_figure(dict, action, figure))
                ret_val.actions.append(action)



        '''for u in range(len(ret_val)):
            for o in range(22):
        for u in range(len(ret_val)):
            for o in range(20):
                print (ret_val[u][o])
            print'''

        return ret_val


    def max_rotation_of_figure(self,num):
        if num == 1:
            return 1
        elif num in [2,3,4]:
            return 2
        else:
            return 4



    def detect_figure(self,avg):
        granice = [[56.5, 45.5, 43.5], [62.5, 34.5, 37.5], [36.5, 53.5, 33.5], [27.5, 53.5, 42.5], [23.5, 41.5, 64.5], [23.5, 37.5, 23.5], [31.75, 31.75, 65.75]]
        num = 0
        for i in granice:
            prosek1 = avg[2]
            prosek2 = avg[1]
            prosek3 = avg[0]
            prva = i[0]
            druga = i[1]
            treca = i[2]
            if (prosek1 > prva) and (prosek1 < prva + 1) and (prosek2 > druga) and (prosek2 < druga + 1) and (
                prosek3 > treca) and (prosek3 < treca + 1):
                return num + 1
            num = num + 1


if __name__ == '__main__':
    tetris = Tetris()
    genetic = None

    dict = {}
    for e in Figure:
        dict[e.name] = e.value

    state_size = 200
    action_size = 38
    agent = DQNAgent(state_size, action_size)
    # agent.load("./save/cartpole-dqn.h5")
    done = False
    episodes = 0

    app = TetrisApp()
    ###############################################################
    ####################Deo bitan za tetris########################
    key_actions = {
        'ESCAPE': app.quit,
        'LEFT': lambda: app.move(-1),
        'RIGHT': lambda: app.move(+1),
        'DOWN': lambda: app.drop(True),
        'UP': app.rotate_stone,
        'p': app.toggle_pause,
        'SPACE': app.start_game,
        'RETURN': app.insta_drop
    }

    app.gameover = False
    app.paused = False

    dont_burn_my_cpu = pygame.time.Clock()
    num=0;
    mon = {'top': 0, 'left': 0, 'width': 200, 'height': 200}
    sct = mss.mss()
    while 1:
        app.screen.fill((0, 0, 0))
        if app.gameover:
            if br == None:
                episodes = 0
                app.gameover = True
                agent.replay(200)
                app.start_game()
                tetris = Tetris()
                continue
            #app.center_msg("""Game Over!\nYour score: %dPress space to continue""" % app.score)
        else:
            if app.paused:
                app.center_msg("Paused")
            else:
                pygame.draw.line(app.screen,
                                 (255, 255, 255),
                                 (app.rlim + 1, 0),
                                 (app.rlim + 1, app.height - 1))
                app.disp_msg("Next:", (
                    app.rlim + cell_size,
                    2))
                app.disp_msg("Score: %d\n\nLevel: %d\nLines: %d" % (app.score, app.level, app.lines),
                             (app.rlim + cell_size, cell_size * 5))
                app.draw_matrix(app.bground_grid, (0, 0))
                app.draw_matrix(app.board, (0, 0))
                app.draw_matrix(app.stone,
                                (app.stone_x, app.stone_y))
                app.draw_matrix(app.next_stone,
                                (cols + 1, 2))

        pygame.display.update()

        # ovo mora da stoji, ne sme se uklanjati
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT + 1:
                app.drop(False)
            elif event.type == pygame.QUIT:
                app.quit()
            elif event.type == pygame.KEYDOWN:
                for key in key_actions:
                    if event.key == eval("pygame.K_" + key):
                        key_actions[key]()

        ######kod ide ovde
        rect = pygame.Rect(0, 0, 280, 56)
        sub = app.screen.subsurface(rect)
        colors = pygame.transform.average_color(sub)
        br = tetris.detect_figure(colors)

        num += 1
        dont_burn_my_cpu.tick(maxfps)

        if br==None:
            app.gameover = True

        if br!=None:

            if episodes == EPISODES:
                app.gameover = True
                br = None
                continue

            action = agent.act(numpy.reshape(tetris.state, [1, state_size]), tetris,dict,br)

            state = tetris.generate_state_based_on_action_and_figure(dict, action, br)

            reward1 = app.score

            for i in range(action[2]):
                app.rotate_stone();

            if action[1] == 0:
                app.move(-1 * action[0])
            elif action[1] == 1:
                app.move(1 * action[0])

            app.insta_drop()

            reward2 = app.score

            reward = 0
            if app.gameover == True:
                reward = -10
            else:
                reward = reward2 - reward1


            agent.remember(numpy.reshape(tetris.state, [1, state_size]), action, reward, numpy.reshape(state, [1, state_size]), app.gameover)

            tetris.state = state


            episodes += 1