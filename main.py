from figures import Figure
from heuristic import Genetic
from state import State
from tetris import Tetris
import time
import copy
import os
import ctypes
import cv2
import mss
import numpy
from gui import TetrisApp, cell_size, cols, maxfps
import pygame
import random
import collections

if __name__ == '__main__':
    tetris = Tetris()

    dict = {}
    for e in Figure:
        dict[e.name] = e.value

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
                    if event.key == eval("pygame.K_" + key):
                        key_actions[key]()

        ######kod ide ovde
        rect = pygame.Rect(0, 0, 280, 56)
        sub = app.screen.subsurface(rect)
        #pygame.image.save(sub, "slik" + str(num) + ".png")
        colors = pygame.transform.average_color(sub)
        br = tetris.detect_figure(colors)

        num += 1
        dont_burn_my_cpu.tick(maxfps)

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
            #time.sleep(0.5)

        num += 1
        dont_burn_my_cpu.tick(maxfps)