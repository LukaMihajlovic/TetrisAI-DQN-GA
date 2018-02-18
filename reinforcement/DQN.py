import random
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from heuristic import Genetic

actions = [
    [0,0,0], [1,0,0], [2,0,0], [3,0,0], [4,0,0], [1,1,0], [2,1,0], [3,1,0], [4,1,0],
    [0,0,1], [1,0,1], [2,0,1], [3,0,1], [4,0,1], [1,1,1], [2,1,1], [3,1,1], [4,1,1], [5,1,1], [6,1,1],
    [0,0,2], [1,0,2], [2,0,2], [3,0,2], [4,0,2], [1,1,2], [2,1,2], [3,1,2], [4,1,2],
    [0,0,3], [1,0,3], [2,0,3], [3,0,3], [4,0,3], [1,1,3], [2,1,3], [3,1,3], [4,1,3],
]

EPISODES = 1000

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=500)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.999
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',optimizer=Adam(lr=self.learning_rate))

        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state1, tetris, dict, figure):
        keys = dict.keys()

        if np.random.rand() <= self.epsilon:
            state = tetris.generate_states_for_action(dict, figure)
            maks_heuristic = -10000
            maks_idx = 0
            for i in range(len(state.states)):

                genetic = Genetic(state.states[i])

                heuristic = genetic.heuristic()
                if heuristic > maks_heuristic:
                    maks_heuristic = heuristic
                    maks_idx = i

            return state.actions[maks_idx]

        act_values = self.model.predict(state1)
        while (1):
            broj = np.argmax(act_values[0])
            label = str(figure) + str(actions[broj][2])
            # ako ne postoji figura, skoci na korekciju, trazi novi random broj
            current_piece_key = filter(lambda x: label in x, keys)
            try:
                current_piece = dict[current_piece_key[0]]
            except IndexError:
                act_values[0][broj] = -1000
                continue
            # ako postoji, vidi je li je to validna akcija za figuru
            if label in ["10", "21", "31", "51", "53", "61", "63", "71", "73"] and actions[broj][0] > 4 and actions[broj][1] == 1:
                act_values[0][broj] = -1000
                continue
            elif label in ["20", "30", "50", "52", "60", "62", "70", "72"] and actions[broj][0] > 3 and actions[broj][1] == 1:
                act_values[0][broj] = -1000
                continue
            elif label in ["40"] and actions[broj][0] > 3:
                act_values[0][broj] = -1000
                continue
            elif label in ["41"] and actions[broj][0] > 3 and actions[broj][1] == 0:
                act_values[0][broj] = -1000
                continue
            return actions[broj]

    def replay(self, batch_size):
        minibatch = []
        if (len(self.memory) < batch_size):
            minibatch = random.sample(self.memory, len(self.memory))
        else:
            minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                #mozda korekcija
                target = (reward + self.gamma * np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][actions.index(action)] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        print self.epsilon