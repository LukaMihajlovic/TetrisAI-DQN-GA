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
                if self.state[j][i] == 1:
                    if j <= highest_available_y:
                        highest_available_y = j-1
                    highest_available.append(j-1)
                    break
                if j == 19:
                    highest_available.append(19)

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

        self.check_for_cleared_lines()

        '''for i in range(20):
            print (self.state[i])
        print'''

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

        #print
        #print len(ret_val)
        return ret_val


    def max_rotation_of_figure(self,num):
        if num == 1:
            return 1
        elif num in [2,3,4]:
            return 2
        else:
            return 4

    def screen_record_efficient(self):
        # 800x600 windowed mode
        user32 = ctypes.windll.user32
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        time.sleep(15)
        osmina = h / 8
        h = h - osmina
        mon = {'top': 165, 'left': 540, 'width': 270, 'height': 80}
        # mon1 = {'top': 100, 'left': w/3 + w/11 , 'width': w/4, 'height': h}

        title = '[MSS] FPS benchmark'
        fps = 0
        sct = mss.mss()
        last_time = time.time()
        num = 0;

        while num != 30:

            img = numpy.asarray(sct.grab(mon))
            # img1 = numpy.asarray(sct.grab(mon1))
            fps += 1

            # cv2.imshow(title, img)
            # cv2.imwrite("slik" + str(num) + ".png", img)
            # cv2.imwrite("skrining.png",img1)
            avg_color_per_row = numpy.average(img, axis=0)
            avg_color = numpy.average(avg_color_per_row, axis=0)
            br = self.detect_figure(avg_color)
            self.generate_states_for_action()

            '''if num > 7 and num < 16:
                pyautogui.press("right", presses=5, interval=0.05)

            if num > 15:
                pyautogui.press("left", presses=5, interval=0.05)
            pyautogui.press("space", presses=1, interval=0.1)'''
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
            num = num + 1
        return fps

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

    dict = {}
    for e in Figure:
        dict[e.name] = e.value

    #tetris.state=tetris.generate_state_based_on_action_and_figure(dict, [0, 1, 0], 3)

    #tetris.state=tetris.generate_state_based_on_action_and_figure(dict, [1, 1, 0], 1)

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
            #time.sleep(200)
            app.center_msg("""Game Over!\nYour score: %dPress space to continue""" % app.score)
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
                    if event.key == eval("pygame.K_"
                                                 + key):
                        key_actions[key]()

        ######kod ide ovde
        rect = pygame.Rect(0, 0, 280, 56)
        sub = app.screen.subsurface(rect)
        #pygame.image.save(sub, "slik" + str(num) + ".png")
        colors = pygame.transform.average_color(sub)
        br = tetris.detect_figure(colors)


        if br==None:
            app.gameover=True

        if br!=None:

            state = tetris.generate_states_for_action(dict,br)

            maks_heuristic = -10000
            maks_idx=0
            for i in range(len(state.states)):

                genetic = Genetic(state.states[i])

                heuristic = genetic.heuristic()
                if heuristic>maks_heuristic:
                    maks_heuristic = heuristic
                    maks_idx = i

            tetris.state = state.states[maks_idx]
            for j in tetris.state:
               print j
            print "+++++++++++"
            tetris.check_for_cleared_lines()

            for r in range(state.actions[maks_idx][2]):
                app.rotate_stone()

            if (state.actions[maks_idx][1] == 0):
                move = -1 * state.actions[maks_idx][0]
                app.move(move)

            if (state.actions[maks_idx][1] == 1):
                move = state.actions[maks_idx][0]
                app.move(move)

            app.insta_drop()
            time.sleep(0.5)

        num += 1
        dont_burn_my_cpu.tick(maxfps)




        #cv2.imwrite()





    #tetris.generate_states_for_action(dict,4)
    #tetris.generate_state_based_on_action_and_figure(dict, [0, 0, 0], 6)
    #tetris.generate_state_based_on_action_and_figure(dict, [3, 1, 0], 4)
    #tetris.generate_state_based_on_action_and_figure(dict, [0, 0, 0], 3)
    #tetris.generate_state_based_on_action_and_figure(dict,  [3 , 0, 0], 1)
    #tetris.generate_state_based_on_action_and_figure(dict,  [1, 0, 1], 2)
    #tetris.generate_state_based_on_action_and_figure(dict, [3, 1, 0], 4)
    #tetris.generate_state_based_on_action_and_figure(dict, [1, 0, 0], 4)
    #tetris.generate_state_based_on_action_and_figure(dict, [1, 0, 0], 4)
    #tetris.generate_state_based_on_action_and_figure(dict, [1, 0, 0], 4)
    #tetris.generate_state_based_on_action_and_figure(dict, [1, 0, 0], 4)
    #tetris.generate_state_based_on_action_and_figure(dict, [1, 0, 0], 4)


    #time.sleep(7)
    #aaaHello world!
    #pyautogui.press("left", presses=3, interval=0.04)
    #pyautogui.press('right', presses=3, interval=0.04)
    #pyautogui.typewrite('Hello world!', interval=0.25)








        #img = numpy.asarray(sct.grab(mon))
        #fps += 1

        # cv2.imshow(title, img)
        #cv2.imwrite("slik" + str(num) + ".png", img)
        # cv2.imwrite("skrining.png",img1)
        #avg_color_per_row = numpy.average(img, axis=0)
        #avg_color = numpy.average(avg_color_per_row, axis=0)
        #br = tetris.detect_figure(avg_color)
        #if br!=None:

        #state = tetris.generate_states_for_action(dict,br[num])



    '''maks_heuristic = -10000
    maks_idx=0
    for i in range(len(state.states)):
        for n in range(22):
            print (state.states[i][n])

        genetic = Genetic(state.states[i])
        print genetic.heuristic()
        print maks_heuristic
        print "++++++++++++++++++++++++++"
        heuristic = genetic.heuristic()
        if heuristic>maks_heuristic:
            maks_heuristic = heuristic
            maks_idx = i

    tetris.state = state.states[maks_idx]
    for m in range(22):
            print (tetris.state[m])'''
    #print "***************************************"
    '''pyautogui.press("up", presses=state.actions[i][2], interval=0.05)
    if (state.actions[i][1] == 0):
        pyautogui.press("left", presses=state.actions[i][0], interval=0.05)

    if (state.actions[i][1] == 1):
        pyautogui.press("right", presses=state.actions[i][0], interval=0.05)

    pyautogui.press("space", presses=1, interval=0.1)'''
    '''if num > 7 and num < 16:
        pyautogui.press("right", presses=5, interval=0.05)

    if num > 15:
        pyautogui.press("left", presses=5, interval=0.05)
    pyautogui.press("space", presses=1, interval=0.1)'''
    '''if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
    num = num + 1
    print num'''
