import pyxel
import pickle #ランキングを保存
import os #ファイルの存在確認
import random

screen_width = 160
screen_height = 120
STONE_iNTERVAL = 5
GAME_OVER_DISPLAY_TIME = 60
START_SCENE = "start"
PLAY_SCENE = "play"
RANKING_SCENE = "ranking"
RANKING_FILE = "ranking.pkl"

class Stone:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def update(self):
        if self.y < screen_height:
            self.y += 2

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 8, 0, 8, 8, pyxel.COLOR_BLACK)

class Item:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True

    def update(self):
        if self.y < screen_height:
            self.y += 2
        else:
            self.active = False

    def draw(self):
        # ここでアイテム画像の座標・サイズを指定
        pyxel.blt(self.x, self.y, 0, 32, 0, 8, 8, pyxel.COLOR_BLACK)

class App:
    def __init__(self):
        pyxel.init(160,120,title="ミニゲーム")
        pyxel.mouse(True)
        pyxel.load("../my_resource.pyxres")
        self.jp_font = pyxel.Font("umplus_j10r.bdf")
        pyxel.playm(0, loop=True)  # BGMを再生
        self.current_scene = START_SCENE
        self.player_x = screen_width // 2
        self.player_y = screen_height * 4 // 5
        self.stones = []
        self.item = None
        self.next_item_timer = random.randint(180, 600)  # 3秒～10秒
        self.is_collision = False
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME
        self.score = 0
        self.stone_speed = 2
        self.stone_interval = STONE_iNTERVAL
        self.ranking = self.load_ranking()
        pyxel.run(self.update,self.draw)

    def load_ranking(self):
        if os.path.exists(RANKING_FILE):
            with open(RANKING_FILE, "rb") as f:
                return pickle.load(f)
        return []

    def save_ranking(self):
        with open(RANKING_FILE, "wb") as f:
            pickle.dump(self.ranking, f)

    def reset_play_sene(self):
        self.player_x = screen_width // 2
        self.player_y = screen_height * 4 // 5
        self.stones = []
        self.item = None
        self.next_item_timer = random.randint(180, 600)
        self.is_collision = False
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME
        self.score = 0
        self.stone_speed = 2
        self.stone_interval = STONE_iNTERVAL

    def update_start_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx = pyxel.mouse_x
            my = pyxel.mouse_y
            # STARTボタンの範囲
            start_btn_x = screen_width//2-20
            start_btn_y = screen_height//2-30
            start_btn_w = 40
            start_btn_h = 16
            # ENDボタンの範囲
            end_btn_x = screen_width//2-20
            end_btn_y = screen_height//2
            end_btn_w = 40
            end_btn_h = 16
            if start_btn_x <= mx <= start_btn_x+start_btn_w and start_btn_y <= my <= start_btn_y+start_btn_h:
                self.reset_play_sene()
                self.current_scene = PLAY_SCENE
            elif end_btn_x <= mx <= end_btn_x+end_btn_w and end_btn_y <= my <= end_btn_y+end_btn_h:
                pyxel.quit()

    def update_ranking_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.current_scene = START_SCENE

    def update_play_scene(self):
        if self.is_collision:
            if self.game_over_display_timer > 0:
                self.game_over_display_timer -= 1
            else:
                # スコアをランキングに追加
                self.ranking.append(self.score)
                self.ranking = sorted(self.ranking, reverse=True)[:3]
                self.save_ranking()
                self.current_scene = RANKING_SCENE
            return

        # スコア加算（生存時間としてカウント）
        self.score += 1

        # 難易度調整：スコアが上がるごとに石のスピードと出現頻度を上げる
        self.stone_speed = 2 + self.score // 300  # 300フレームごとに+1
        self.stone_interval = max(1, STONE_iNTERVAL - self.score // 300)  # 最小1まで減少

        # プレイヤーの移動
        if pyxel.btn(pyxel.KEY_RIGHT) and self.player_x < screen_width - 20:
            self.player_x += 1
        elif pyxel.btn(pyxel.KEY_LEFT) and self.player_x > 5:
            self.player_x -= 1

        # 石の追加
        if pyxel.frame_count % self.stone_interval == 0:
            self.stones.append(Stone(pyxel.rndi(0,screen_width-8),0))

        # 石の落下
        for stone in self.stones.copy():
            stone.y += self.stone_speed  # スピードを反映
            # 衝突
            if (self.player_x <= stone.x <= self.player_x+10 and self.player_y <= stone.y <= self.player_y+7):
                self.is_collision = True
            # 画面外に出た石の削除
            if stone.y >= screen_height:
                self.stones.remove(stone)

        # アイテム出現タイマー
        if self.item is None:
            self.next_item_timer -= 1
            if self.next_item_timer <= 0:
                self.item = Item(pyxel.rndi(0, screen_width-8), 0)
        else:
            self.item.update()
            # プレイヤーとアイテムの当たり判定
            if (self.player_x <= self.item.x <= self.player_x+10 and
                self.player_y <= self.item.y <= self.player_y+7):
                self.score += 100
                self.item = None
                self.next_item_timer = random.randint(180, 600)
            elif not self.item.active:
                self.item = None
                self.next_item_timer = random.randint(180, 600)

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if self.current_scene == START_SCENE:
            self.update_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.update_play_scene()
        elif self.current_scene == RANKING_SCENE:
            self.update_ranking_scene()

    def draw_start_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        pyxel.text(25, 15, "がんばれ!! スライムくん", pyxel.COLOR_YELLOW,self.jp_font)
        
        pyxel.blt(100 , 100, 0, 16, 0, 16, 16, pyxel.COLOR_BLACK)
        # STARTボタン描画
        start_btn_x = screen_width//2-15
        start_btn_y = screen_height//2-25
        start_btn_w = 30
        start_btn_h = 10
        pyxel.rect(start_btn_x, start_btn_y, start_btn_w, start_btn_h, pyxel.COLOR_GREEN)
        pyxel.text(start_btn_x+6, start_btn_y+3, "START", pyxel.COLOR_WHITE)
        # ENDボタン描画
        end_btn_x = screen_width//2-15
        end_btn_y = screen_height//2-5
        end_btn_w = 30
        end_btn_h = 10
        pyxel.rect(end_btn_x, end_btn_y, end_btn_w, end_btn_h, pyxel.COLOR_RED)
        pyxel.text(end_btn_x+9, end_btn_y+3, "END", pyxel.COLOR_WHITE)

    def draw_ranking_scene(self):
        pyxel.cls(pyxel.COLOR_NAVY)
        pyxel.text(screen_width//2-25, 20, "SCORE RANKING", pyxel.COLOR_YELLOW)
        for i, score in enumerate(self.ranking[:3]):
            pyxel.text(screen_width//2-20, 40+20*i, f"{i+1} : {score}点", pyxel.COLOR_WHITE)
        pyxel.text(screen_width//2-40, 100, "クリックでスタート画面へ", pyxel.COLOR_CYAN)

    def draw_play_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        for stone in self.stones:
            stone.draw()
        # アイテムの描画
        if self.item is not None:
            self.item.draw()
        # プレイヤーの描画
        pyxel.blt(self.player_x, self.player_y, 0, 16, 0, 16, 16, pyxel.COLOR_BLACK)
        # スコアを表示
        pyxel.text(5, 5, f"Score: {self.score}", pyxel.COLOR_WHITE)
        if self.is_collision:
            pyxel.text(screen_width//2-20, screen_height//2, "GAME OVER", pyxel.COLOR_RED)

    def draw(self):
        pyxel.cls(0)
        pyxel.text(10, 10, f"scene: {self.current_scene}", 7)
        if self.current_scene == START_SCENE:
            self.draw_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.draw_play_scene()
        elif self.current_scene == RANKING_SCENE:
            self.draw_ranking_scene()

App()
