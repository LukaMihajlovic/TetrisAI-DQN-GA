from Figures import Figure
from genetic import Genetic
from state import State
import time
import pyautogui
import copy
from selenium import webdriver
import os
from selenium.webdriver.chrome.options import Options
import pyautogui
import ctypes
import cv2
import mss
import numpy
from pynput.keyboard import Key, Controller


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

        self.keyboard = Controller()

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

        if (all(x == highest_available[0] for x in highest_available)):
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

        elif label == "51":
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

        elif label == "63":
            if highest_available[0] < highest_available[1]:
                if (highest_available[1] - highest_available[0]) >= 2:
                    highest_available_y += 2
                else:
                    highest_available_y += 1

        elif label == "71":
            if highest_available[1] < highest_available[0]:
                highest_available_y += 1

        elif label == "72":
            if highest_available[0] < highest_available[1] and highest_available[2] < highest_available[1] and highest_available[0] == highest_available[2]:
                highest_available_y += 1

        elif label == "73":
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


        '''for i in range(20):
            print (self.state[i])
        print'''

        return ret_val



    def coordinate(self, label):
        if label == "41":
            return 6
        elif label in ["10", "21", "31", "41", "51", "61", "71"]:
            return 5
        else:
            return 4

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
            br = detect_figure(avg_color)
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
        granice = [[7, 21, 23], [7, 7, 23], [12, 23, 7], [23, 21, 7], [23, 16, 7], [7, 18, 23], [23, 7, 20]]
        num = 0
        for i in granice:
            prosek1 = avg[0]
            prosek2 = avg[1]
            prosek3 = avg[2]
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


    '''tetris.state=tetris.generate_state_based_on_action_and_figure(dict, [0, 0, 0], 4)

    tetris.state=tetris.generate_state_based_on_action_and_figure(dict, [2, 1, 0], 1)
    tetris.state=tetris.generate_state_based_on_action_and_figure(dict, [3, 1, 0], 1)'''








    #for i in range(20):
    #    print tetris.state[i]
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


    #time.sleep(1)
    '''executable_path = "chromedriver.exe"
    os.environ["webdriver.chrome.driver"] = executable_path
    chop = Options()
    chop.add_extension("Adblock-Plus_v1.12.4.crx")
    chop.add_argument("start-maximized")
    chop.add_argument("hide-scrollbars")
    driver = webdriver.Chrome(executable_path=executable_path, chrome_options=chop)
    driver.maximize_window()
    driver.set_page_load_timeout(30)
    driver.get("https://tetris.com/play-tetris/?utm_source=top_nav_link&utm_medium=webnav&utm_campaign=playNow_btm_tst&utm_content=text_play_now")
    time.sleep(10)
    user32 = ctypes.windll.user32
    w = user32.GetSystemMetrics(0)
    h = user32.GetSystemMetrics(1)
    mon = {'top': 165, 'left': 540, 'width': 270, 'height': 80}'''

    sct = mss.mss()

    # 800x600 windowed mode

    num = 0;
    #pyautogui.press("space", presses=1, interval=0.1)

    num=0
    while num != 1127:

        #if all(x == 0 for x in tetris.state[19]):
        #    pyautogui.click(610, 380)
        #img = numpy.asarray(sct.grab(mon))
        #fps += 1

        # cv2.imshow(title, img)
        #cv 2.imwrite("slik" + str(num) + ".png", img)
        # cv2.imwrite("skrining.png",img1)
        #avg_color_per_row = numpy.average(img, axis=0)
        #avg_color = numpy.average(avg_color_per_row, axis=0)
        #br = tetris.detect_figure(avg_color)
        br=[2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6,2,4,5,3,6,7,2,1,3,4,6,2,4,5,6,2,6,4,3,2,7,6,5,4,1,4,7,6,5,4,6,3,2,1,7,6,5,4,2,3,1,7,7,4,1,2,6]
        print len(br)
        if br!=None:

            state = tetris.generate_states_for_action(dict,br[num])



            maks_heuristic = -10000
            maks_idx=0
            for i in range(len(state.states)):

                genetic = Genetic(state.states[i])

                heuristic = genetic.heuristic()
                if heuristic>maks_heuristic:
                    maks_heuristic = heuristic
                    maks_idx = i

            tetris.state = state.states[maks_idx]
            #for j in tetris.state:
            #   print j
            #print "+++++++++++"
            tetris.check_for_cleared_lines()


            '''pyautogui.press("up", presses=state.actions[maks_idx][2], interval=0.15)

            for u in range(state.actions[maks_idx][2]):
                tetris.keyboard.press(Key.up)
                tetris.keyboard.release(Key.up)
                time.sleep(0.15)
                #pyautogui.press("up")

            if (state.actions[maks_idx][1] == 0):
                pyautogui.press("left", presses=state.actions[maks_idx][0], interval=0.15)
                for l in range(state.actions[maks_idx][0]):
                    tetris.keyboard.press(Key.left)
                    tetris.keyboard.release(Key.left)
                    time.sleep(0.15)

                    pyautogui.press("left")'''


            '''if (state.actions[maks_idx][1] == 1):
                pyautogui.press("right", presses=state.actions[maks_idx][0], interval=0.15)
                for r in range(state.actions[maks_idx][0]):
                    tetris.keyboard.press(Key.right)
                    tetris.keyboard.release(Key.right)
                    time.sleep(0.15)
                    #pyautogui.press("right")

            tetris.keyboard.press(Key.space)
            tetris.keyboard.release(Key.space)
            time.sleep(0.12)'''

            #pyautogui.press("space")

            '''if num > 7 and num < 16:
                pyautogui.press("right", presses=5, interval=0.05)
        
            if num > 15:
                pyautogui.press("left", presses=5, interval=0.05)
            pyautogui.press("space", presses=1, interval=0.1)'''
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
            num = num + 1
            print num
    for i in range(20):
        print 
