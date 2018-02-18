from figures import Figure
from state import State
import copy
import mss
import numpy
from gui7x7 import TetrisApp, cell_size, cols, maxfps
import pygame
from QL import QLAgent
import random
import collections

# Just disables the warning, doesn't enable AVX/FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

actions = [
    [0,0,0], [1,0,0], [2,0,0], [1,1,0], [2,1,0], [3,1,0],
    [0,0,1], [1,0,1], [2,0,1], [1,1,1], [2,1,1], [3,1,1], [4,1,1], [5,1,1],
    [0,0,2], [1,0,2], [2,0,2], [1,1,2], [2,1,2], [3,1,2],
    [0,0,3], [1,0,3], [2,0,3], [1,1,3], [2,1,3], [3,1,3]
]


EPISODES = 1000

class Tetris:

    def __init__(self):

        #reprezentacija stanja
        self.state = []
        for i in range(14):
            self.state.append([])
            for j in range(7):
                self.state[i].append(0)

        self.cleared_lines = 0
        self.bag = [1, 2, 3, 4, 5, 6, 7]
        random.shuffle(self.bag)
        self.sequence = collections.deque(self.bag)

        self.game_over = False

    def stone_next(self):
        num = self.sequence.popleft()
        if not self.sequence:
            bag = [1, 2, 3, 4, 5, 6, 7]
            random.shuffle(bag)
            self.sequence.extend(bag)
        return num

    def row_empty(self,num):

        for i in range(7):
            if self.state[num][i] == 1:
                return False

        return True

    def end_game(self):
        return not self.row_empty(0) or not self.row_empty(1)

    def generate_state_based_on_action_and_figure(self, dict, action, figure):

        keys = dict.keys()

        label = str(figure) + str(action[2])

        current_piece_key = filter(lambda x: label in x, keys)
        current_piece = dict[current_piece_key[0]]

        starting_coordinate = self.coordinate(label)
        width = self.piece_width(label)
        height = len(current_piece)

        highest_available_y = 14
        highest_available = []

        highest_available_x = 0
        if action[1] == 1:
            highest_available_x = starting_coordinate + action[0]
        else:
            highest_available_x = starting_coordinate - action[0]

        #pronalazenje najvise slobodne tacke na sirini figure
        for i in range(highest_available_x-1, highest_available_x-1+width):
            for j in range(14):
                if self.state[j][i] == 1:
                    if j <= highest_available_y:
                        highest_available_y = j-1
                    highest_available.append(j-1)
                    break
                if j == 13:
                    highest_available.append(13)

        if (all(x==highest_available[0] for x in highest_available)):
            if (highest_available[0] == 13):
                highest_available_y = 13

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
        #self.check_for_cleared_lines()

        return ret_val



    def coordinate(self, label):
        if label in ["41", "40"]:
            return 2
        else:
            return 3

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
        ret_val = 0
        for i in range(14):
            if all(x == 1 for x in self.state[i]):
                self.state.pop(i)
                self.state.insert(0, [0,0,0,0,0,0,0])
                self.cleared_lines += 1
                ret_val += 1

        return ret_val


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
            max_right = 7 - current_piece_right_position

            for j in range(max_left+1):
                action = [j, 0, i]
                ret_val.states.append(self.generate_state_based_on_action_and_figure(dict, action, figure))
                ret_val.actions.append(action)
            for k in range(1,max_right+1):
                action = [k, 1, i]
                ret_val.states.append(self.generate_state_based_on_action_and_figure(dict, action, figure))
                ret_val.actions.append(action)

        return ret_val


    def max_rotation_of_figure(self,num):
        if num == 1:
            return 1
        elif num in [2,3,4]:
            return 2
        else:
            return 4



    def detect_figure(self,avg):
        granice = [[73.5, 57.5, 54.5], [81.5, 42.5, 45.5], [44.5, 68.5, 40.5], [32.5, 69.5, 53.5], [25.5, 51.5, 84.5], [26.5, 45.5, 25.5], [38.5, 38.5, 86.5]]
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

    dict = {}
    for e in Figure:
        dict[e.name] = e.value

    agent = QLAgent(26)
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
    write_to_file_step = 0.95
    broj_ociscenih_linija_file = 0
    broj_partija_file = 0
    while 1:
        app.screen.fill((0, 0, 0))
        if app.gameover:
            if br == None:
                broj_ociscenih_linija_file += app.lines
                broj_partija_file += 1
                app.gameover = True
                app.start_game()
                tetris = Tetris()
                agent.epsilon *= 0.9995

                #belezenje rezultata
                if agent.epsilon < write_to_file_step:
                    with open("q-learning-results.txt", "a") as myfile:
                        myfile.write("Broj ociscenih linija za exploration rate veci od " + str(write_to_file_step) + " je " + str(broj_ociscenih_linija_file) + " u broju partija " + str(broj_partija_file) + "\n")
                        write_to_file_step = write_to_file_step - 0.05
                        broj_ociscenih_linija_file = 0
                        broj_partija_file = 0

                print agent.epsilon
                episodes = 0
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
        rect = pygame.Rect(0, 0, 196, 56)
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

            action = agent.choose_action(hash(tuple(numpy.reshape(tetris.state, [1,98])[0])), dict, br, tetris)

            next_state = tetris.generate_state_based_on_action_and_figure(dict, action, br)

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
                reward = -500
            else:
                reward = reward2 - reward1

            agent.learn(hash(tuple(numpy.reshape(tetris.state, [1,98])[0])), actions.index(action), reward, hash(tuple(numpy.reshape(next_state, [1,98])[0])), app.gameover)

            tetris.state = next_state
            tetris.check_for_cleared_lines()

            episodes += 1