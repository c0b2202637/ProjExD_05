import math
import random
import sys
import time
from typing import Any

import pygame as pg
from pygame.sprite import AbstractGroup

WIDTH = 800
HEIGHT = 600

def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，こうかとん，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT-200 < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


#基本機能
class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"ex04/fig/{num}.png"), 0, 1.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 0, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 0, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, 0, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 0, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, 0, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, 0, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.state = "normal"
        self.hyper_life = -1

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"ex04/fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)
    def change_state(self, state: str, hyper_life: int):
        """
        hyperモードとノーマルモードを切り替える
        """
        self.state = state
        self.hyper_life = hyper_life
    def tick_move(self):
        """
        重力
        """
        self.rect.move_ip(0, 3)




    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(self.rect) != (True, True):
            for k, mv in __class__.delta.items():
                if key_lst[k]:
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        if self.state == "hyper":
            self.hyper_life -= 1
            self.image = pg.transform.laplacian(self.image)
        if self.hyper_life < 0:
            self.change_state("normal",-1)
        screen.blit(self.image, self.rect)
    
    def get_direction(self) -> tuple[int, int]:
        return self.dire
    

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
    bird = Bird(3, (200, HEIGHT-225))


    zimen = pg.Surface((800,200))
    pg.draw.rect(zimen,(0,0,0),(0,0,800,200))

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
            #if event.type == pg.KEYDOWN and event.key == pg.K_f:
                #这里

        key_lst = pg.key.get_pressed()

        screen.fill((255, 255, 255))
        screen.blit(zimen, (0, HEIGHT-200))

        bird.update(key_lst, screen)
        bird.tick_move()  # 重力

        pg.display.update()
        tmr += 1
        clock.tick(100)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()