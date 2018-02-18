import numpy as np
import pandas as pd
from copy import deepcopy
from heuristic import Genetic

actions = [
    [0,0,0], [1,0,0], [2,0,0], [1,1,0], [2,1,0], [3,1,0],
    [0,0,1], [1,0,1], [2,0,1], [1,1,1], [2,1,1], [3,1,1], [4,1,1], [5,1,1],
    [0,0,2], [1,0,2], [2,0,2], [1,1,2], [2,1,2], [3,1,2],
    [0,0,3], [1,0,3], [2,0,3], [1,1,3], [2,1,3], [3,1,3]
]

class QLAgent:
    def __init__(self, action_number, learning_rate=0.2, reward_decay=0.8, e_greedy=1.0):
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.actions = []
        for i in range(action_number):
            self.actions.append(i)
        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)

    def choose_action(self, observation, dict, figure, tetris):
        keys = dict.keys()

        self.check_state_exist(observation)
        # action selection
        if np.random.rand() <= self.epsilon:
            state = tetris.generate_states_for_action(dict, figure)
            maks_heuristic = -10000
            maks_idx = 0
            for i in range(len(state.states)):

                heuristic = Genetic(state.states[i])

                heuristic = heuristic.heuristic()
                if heuristic > maks_heuristic:
                    maks_heuristic = heuristic
                    maks_idx = i

            return state.actions[maks_idx]
        else:
            state_action = self.q_table.loc[observation, :]
            state_action = state_action.reindex(np.random.permutation(state_action.index))
            state_action2 = deepcopy(state_action)
            while 1:
                # kopija
                action = state_action2.idxmax(0)

                label = str(figure) + str(actions[action][2])
                # ako ne postoji figura, skoci na korekciju, trazi novi random broj
                current_piece_key = filter(lambda x: label in x, keys)
                try:
                    current_piece = dict[current_piece_key[0]]
                except IndexError:
                    state_action2[action] = -1000
                    continue
                # ako postoji, vidi je li je to validna akcija za figuru
                if label in ["10", "21", "31", "51", "53", "61", "63", "71", "73"] and actions[action][0] > 3 and \
                                actions[action][1] == 1:
                    state_action2[action] = -1000
                    continue
                elif label in ["20", "30", "50", "52", "60", "62", "70", "72"] and actions[action][0] > 2 and \
                                actions[action][1] == 1:
                    state_action2[action] = -1000
                    continue
                elif label in ["40"] and actions[action][0] > 1 and actions[action][1] == 0:
                    state_action2[action] = -1000
                    continue
                elif label in ["40"] and actions[action][0] > 2 and actions[action][1] == 1:
                    state_action2[action] = -1000
                    continue
                elif label in ["41"] and actions[action][0] > 1 and actions[action][1] == 0:
                    state_action2[action] = -1000
                    continue
                return actions[action]

    def learn(self, s, a, r, s_, done):
        self.check_state_exist(s_)
        q_predict = self.q_table.loc[s, a]
        if not done:
            q_target = r + self.gamma * self.q_table.loc[s_, :].max()
        else:
            q_target = r
        self.q_table.loc[s, a] += self.lr * (q_target - q_predict)

    def check_state_exist(self, state):
        if state not in self.q_table.index:
            # append new state to q table
            self.q_table = self.q_table.append(
                pd.Series(
                    [0] * len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            )