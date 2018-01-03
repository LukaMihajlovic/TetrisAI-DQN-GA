from Figures import Figure
import time
import pyautogui

class Tetris:

    def __init__(self):

        #reprezentacija stanja
        self.state = []
        for i in range(22):
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

        highest_available_y = 22
        highest_available = []

        highest_available_x = 0
        if (action[1] == 1):
            highest_available_x = starting_coordinate + action[0]
        else:
            highest_available_x = starting_coordinate - action[0]

        #pronalazenje najvise slobodne tacke na sirini figure
        for i in range(highest_available_x-1, highest_available_x-1+width):
            for j in range(22):
                if self.state[j][i] == 1:
                    if (j < highest_available_y):
                        highest_available_y = j-1
                    highest_available.append(j-1)
                    break
                if j == 21:
                    highest_available_y = 21
                    highest_available.append(21)

        if label == "20":
            if (highest_available[0] < highest_available[1] and highest_available[0] < highest_available[2]):
                highest_available_y += 1

        elif label == "21":
            if (highest_available[1] < highest_available[0]):
                highest_available_y += 1

        elif label == "30":
            if (highest_available[2] < highest_available[1] and highest_available[2] < highest_available[0]):
                highest_available_y += 1

        elif label == "31":
            if (highest_available[0] < highest_available[1]):
                highest_available_y += 1

        elif label == "51":
            if (highest_available[1] < highest_available[0]):
                if ((highest_available[0] - highest_available[1]) == 2):
                    highest_available_y += 2
                else:
                    highest_available_y += 1

        elif label == "52":
            if (highest_available[0] < highest_available[1] and highest_available[0] < highest_available[2]):
                highest_available_y += 1

        elif label == "62":
            if (highest_available[2] < highest_available[1] and highest_available[2] < highest_available[0]):
                highest_available_y += 1

        elif label == "63":
            if (highest_available[0] < highest_available[1]):
                if ((highest_available[1] - highest_available[0]) == 2):
                    highest_available_y += 2
                else:
                    highest_available_y += 1

        elif label == "71":
            if (highest_available[1] < highest_available[0]):
                highest_available_y += 1

        elif label == "72":
            if (highest_available[0] < highest_available[1] and highest_available[2] < highest_available[1]
                and highest_available[0] == highest_available[2]):
                highest_available_y += 1

        else:
            if (highest_available[0] < highest_available[1]):
                highest_available_y += 1

        # postavljanje figure
        for i in range(len(current_piece) - 1, -1, -1):
            for j in range(len(current_piece[i]) - 1, -1, -1):
                if current_piece[i][j] == 1:
                    self.state[highest_available_y - (height - 1) + i][highest_available_x - 1 + j] = 1

        for i in range(22):
            print (self.state[i])

        #ciscenje
        highest_available = []



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



if __name__ == '__main__':
    tetris = Tetris()

    dict = {}
    for e in Figure:
        dict[e.name] = e.value

    tetris.generate_state_based_on_action_and_figure(dict, [2, 1, 0], 4)
    tetris.generate_state_based_on_action_and_figure(dict, [2, 1, 0], 4)
    tetris.generate_state_based_on_action_and_figure(dict, [0, 0, 1], 2)
    tetris.generate_state_based_on_action_and_figure(dict, [2, 1, 0], 2)
    tetris.generate_state_based_on_action_and_figure(dict, [0, 1, 1], 5)

    #time.sleep(7)

    #pyautogui.press("left", presses=2, interval=0.02)
    #pyautogui.press("space", presses=1, interval=0.02)


    time.sleep(1)
