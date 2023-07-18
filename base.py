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
        self.beam_mode = False

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

    def change_beam_mode(self): #ビームを出せるかどうか決定
        if self.beam_mode == False:
            self.beam_mode = True
        else:
            self.beam_mode = False

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
class Star(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/star.png"), 0, 0.1)
        self.rect = self.image.get_rect()
        self.rect.center = (1000, HEIGHT-225)

    def change_img(self, num: int, screen: pg.Surface):
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect.center = (self.rect.centerx - 5,self.rect.centery)




#障害物破壊
class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = bird.get_direction()
        angle = math.degrees(math.atan2(0, self.vx)) #横に固定する
        self.image = pg.transform.rotozoom(pg.image.load(f"ex04/fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 5

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()

#地形生成



def main():
    pg.display.set_caption("走れこうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    clock = pg.time.Clock()
    bird = Bird(3, (200, HEIGHT-225))
    star = pg.sprite.Group()

    tmr = 0
    bird.change_beam_mode() #呼び出すたびに変更.これでTrue    tmr = 0
    zimen = pg.Surface((800,200))
    pg.draw.rect(zimen,(0,0,0),(0,0,800,200))
    beams = pg.sprite.Group()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return

        key_lst = pg.key.get_pressed()
        if tmr == 200:
            star.add(Star())
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN and len(beams)<1 and bird.beam_mode:
                beams.add(Beam(bird))

        screen.fill((255, 255, 255))
        screen.blit(zimen, (0, HEIGHT-200))
        for star0 in pg.sprite.spritecollide(bird, star, True):
            bird.change_state("hyper",500)
        key_lst = pg.key.get_pressed()

        bird.update(key_lst, screen)

        star.update()
        star.draw(screen)
        beams.update()
        beams.draw(screen)
        pg.display.update()
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()