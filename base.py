import math
import random
import sys
import time
from typing import Any

import pygame as pg
from pygame.sprite import AbstractGroup

WIDTH = 800
HEIGHT = 600

#基本機能
#class base:


#障害物



#スコア走行距離



#空飛ぶ


#無敵



#障害物破壊


#地形生成



def main():
    pg.display.set_caption("走れこうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    clock = pg.time.Clock()
    tmr = 0
    zimen = pg.Surface((800,200))
    pg.draw.rect(zimen,(0,0,0),(0,0,800,200))
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
        screen.fill((255, 255, 255))
        screen.blit(zimen, (0, HEIGHT-200))
        pg.display.update()
        tmr += 1
        clock.tick(10)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()