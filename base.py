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

    JUMP_HEIGHT = 200  #ジャンプの高さ
    JUMP_SPEED = 5  #ジャンプの上昇する速度
    JUMP_DURATION = 450  #ジャンプの持続時間(フレーム数)
    PAUSE_DURATION = 15  #頂点での停止時間

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"ex04/fig/{num}.png"), 0, 2.0)
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

        self.is_jumping = False  #ジャンプ中かどうか。ジャンプ中はTrue、それ以外はFalse。
        self.jump_count = 0  #ジャンプの進行している長さ
        self.jump_timer = 0  #ジャンプの経過フレーム数
        self.pause_timer = 0  #頂点での一時停止時のフレーム数
        self.original_y = HEIGHT - 250  #キャラクターの元の位置の座標
        self.is_returning = False  #元の位置に戻るタイミング。上昇時はFalse、落下時はTrue。




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

    def jump(self):
        if self.is_jumping:  #  ジャンプをしたとき
            if self.jump_count >= self.JUMP_HEIGHT:  #ジャンプの頂点に達した場合
                if self.pause_timer >= self.PAUSE_DURATION:  #頂点で一時停止時間を終えた場合
                    self.is_jumping = False  #ジャンプ終了
                    self.jump_count = 0  #ジャンプの進行をリセット
                    self.jump_timer = 0  #ジャンプ中のフレーム数をリセット
                    self.pause_timer = 0  #頂点での一時停止中のフレーム数をリセット
                    self.is_returning = True  #元の位置に戻るようにself.is_returningをTrueにする。
                else:
                    self.pause_timer += 1  #頂点での一時停止中の時間を計測
            else:
                self.rect.move_ip(0, -self.JUMP_SPEED)  #キャラクターを上に移動
                self.jump_count += self.JUMP_SPEED  #上昇度を増加させる
                self.jump_timer += 1  #ジャンプ中のフレーム数を増加
        elif self.is_returning:  #self.is_returningがTrue
            if self.rect.y < self.original_y:  #元の位置に達していない場合
                self.rect.move_ip(0, self.JUMP_SPEED)  #下向きに移動
            else:
                self.rect.y = self.original_y  #元の位置に戻る
                self.is_returning = False  #落下移動の終了
        else:  #ジャンプ開始の処理
            pressed_keys = pg.key.get_pressed()  #入力キーの入手
            if pressed_keys[pg.K_SPACE] and self.jump_count == 0 and self.jump_timer == 0:  #ジャンプの開始条件
                self.is_jumping = True  #ジャンプ開始



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
        
        self.jump()
        
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
    bird = Bird(3, (200, HEIGHT-225))
    tmr = 0
    zimen = pg.Surface((800,200))
    pg.draw.rect(zimen,(0,0,0),(0,0,800,200))
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
        screen.fill((255, 255, 255))
        screen.blit(zimen, (0, HEIGHT-200))

        key_lst = pg.key.get_pressed()

        bird.update(key_lst, screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()