import pyxel
import random

screen_width = 160
screen_height = 120
STONE_iNTERVAL = 5
GAME_OVER_DISPLAY_TIME = 60
START_SCENE = "start"
PLAY_SCENE = "play"
RANKING_SCENE = "ranking"
RANKING_FILE = "ranking.pkl"
MANUAL_SCENE = "manual"  

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
            self.y +=  1
        else:
            self.active = False

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 32, 0, 8, 8, pyxel.COLOR_BLACK)

class HeartItem(Item):
    def draw(self):
        pyxel.blt(self.x, self.y, 0, 40, 0, 8, 8, pyxel.COLOR_BLACK)

class App:
    def __init__(self):
        pyxel.init(160,120,title="ミニゲーム")
        pyxel.mouse(True)
        pyxel.load("my_resource.pyxres")
        self.jp_font = pyxel.Font("umplus_j10r.bdf")
        pyxel.playm(0, loop=True)  
        self.current_scene = START_SCENE
        self.player_x = screen_width // 2
        self.player_y = screen_height * 4 // 5
        self.stones = []
        self.item = None
        self.heart_item = None
        self.next_item_timer = random.randint(60, 120)      
        self.next_heart_timer = random.randint(20, 40)    
        self.is_collision = False
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME
        self.score = 0
        self.stone_speed = 2
        self.stone_interval = STONE_iNTERVAL
        self.ranking = self.load_ranking()
        self.item_get_timer = 0  
        self.life = 1  
        self.new_rank_index = None  
        self.reset_message_timer = 0  
        pyxel.run(self.update, self.draw)

    def load_ranking(self):
        return []

    def save_ranking(self):
        pass

    def reset_play_sene(self):
        self.player_x = screen_width // 2
        self.player_y = screen_height * 4 // 5
        self.stones = []
        self.item = None
        self.heart_item = None
        self.next_item_timer = random.randint(60, 120)
        self.next_heart_timer = random.randint(20, 40)
        self.is_collision = False
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME
        self.score = 0
        self.stone_speed = 2
        self.stone_interval = STONE_iNTERVAL
        self.item_get_timer = 0  
        self.life = 1

    def reset_ranking(self):
        self.ranking = []
        if os.path.exists(RANKING_FILE):
            os.remove(RANKING_FILE)
        self.reset_message_timer = 30  

    def update(self):
        if self.reset_message_timer > 0:
            self.reset_message_timer -= 1
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        if self.current_scene == START_SCENE:
            self.update_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.update_play_scene()
        elif self.current_scene == RANKING_SCENE:
            self.update_ranking_scene()
        elif self.current_scene == MANUAL_SCENE:
            self.update_manual_scene()

    def update_start_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx = pyxel.mouse_x
            my = pyxel.mouse_y
           
            start_btn_x = screen_width//2-10
            start_btn_y = screen_height//2-10
            start_btn_w = 30
            start_btn_h = 10
            
            end_btn_x = screen_width//2-6
            end_btn_y = screen_height//2+3
            end_btn_w = 30
            end_btn_h = 10
            
            manual_btn_x = screen_width//2-8
            manual_btn_y = screen_height//2+16
            manual_btn_w = 30
            manual_btn_h = 10
           
            reset_btn_x = screen_width//2-80
            reset_btn_y = screen_height//2+50
            reset_btn_w = 10
            reset_btn_h = 10

            if start_btn_x <= mx <= start_btn_x+start_btn_w and start_btn_y <= my <= start_btn_y+start_btn_h:
                self.reset_play_sene()
                self.current_scene = PLAY_SCENE
            elif end_btn_x <= mx <= end_btn_x+end_btn_w and end_btn_y <= my <= end_btn_y+end_btn_h:
                pyxel.quit()
            elif manual_btn_x <= mx <= manual_btn_x+manual_btn_w and manual_btn_y <= my <= manual_btn_y+manual_btn_h:
                self.current_scene = MANUAL_SCENE
            elif reset_btn_x <= mx <= reset_btn_x+reset_btn_w and reset_btn_y <= my <= reset_btn_y+reset_btn_h:
                self.reset_ranking()

    def update_manual_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.current_scene = START_SCENE

    def update_ranking_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.current_scene = START_SCENE
            self.new_rank_index = None  

    def update_play_scene(self):
        if self.is_collision:
            if self.game_over_display_timer > 0:
                self.game_over_display_timer -= 1
            else:
                
                old_ranking = self.ranking.copy()
                self.ranking.append(self.score)
                self.ranking = sorted(self.ranking, reverse=True)[:3]
                self.save_ranking()
                
                self.new_rank_index = None
                for i, score in enumerate(self.ranking):
                    if score == self.score and (len(old_ranking) <= i or old_ranking[i] != self.score):
                        self.new_rank_index = i
                        break
                self.current_scene = RANKING_SCENE
            return

        
        self.score += 1

        
        self.stone_speed = min(5, 2 + self.score // 400)  
        self.stone_interval = max(1, STONE_iNTERVAL - self.score // 400) 

        
        if pyxel.btn(pyxel.KEY_RIGHT) and self.player_x < screen_width - 20:
            self.player_x += 2  
        elif pyxel.btn(pyxel.KEY_LEFT) and self.player_x > 5:
            self.player_x -= 2 

        
        if pyxel.frame_count % self.stone_interval == 0:
            self.stones.append(Stone(pyxel.rndi(0,screen_width-8),0))

        
        for stone in self.stones.copy():
            stone.y += self.stone_speed
            if (self.player_x <= stone.x <= self.player_x+10 and self.player_y <= stone.y <= self.player_y+7):
                self.life -= 1
                self.stones.remove(stone)
                if self.life <= 0:
                    self.is_collision = True
            elif stone.y >= screen_height:
                self.stones.remove(stone)

        
        if self.item is None:
            self.next_item_timer -= 1
            if self.next_item_timer <= 0:
                self.item = Item(pyxel.rndi(0, screen_width-8), 0)
                self.next_item_timer = random.randint(60, 120)
        else:
            self.item.update()
            if (self.player_x < self.item.x + 8 and self.player_x + 16 > self.item.x and
                self.player_y < self.item.y + 8 and self.player_y + 16 > self.item.y):
                self.score += 100
                self.item = None
                self.next_item_timer = random.randint(60, 120)
                self.item_get_timer = 60
            elif not self.item.active:
                self.item = None
                self.next_item_timer = random.randint(60, 120)

        
        if self.heart_item is None:
            self.next_heart_timer -= 1
            if self.next_heart_timer <= 0:
                self.heart_item = HeartItem(pyxel.rndi(0, screen_width-8), 0)
                self.next_heart_timer = random.randint(20, 40)
        else:
            self.heart_item.update()
            if (self.player_x < self.heart_item.x + 8 and self.player_x + 16 > self.heart_item.x and
                self.player_y < self.heart_item.y + 8 and self.player_y + 16 > self.heart_item.y):
                self.life += 1
                self.heart_item = None
            elif not self.heart_item.active:
                self.heart_item = None

        
        if self.item_get_timer > 0:
            self.item_get_timer -= 1

    def draw_start_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        pyxel.text(25, 30, "がんばれ!! スライムくん", pyxel.COLOR_YELLOW, self.jp_font)
        pyxel.text(85, 100, "♪BGM:Mini Dessert", pyxel.COLOR_PEACH)
        pyxel.text(25, 110, "MOMIZIzm MUSIC(momijiba)Free BGM", pyxel.COLOR_PEACH)
        pyxel.blt(110 , 70, 0, 16, 0, 16, 16, pyxel.COLOR_BLACK)
        
        start_btn_x = screen_width//2-10
        start_btn_y = screen_height//2-10
        pyxel.text(start_btn_x, start_btn_y, "START", pyxel.COLOR_WHITE)
        
        end_btn_x = screen_width//2-6
        end_btn_y = screen_height//2+3
        pyxel.text(end_btn_x, end_btn_y, "END", pyxel.COLOR_WHITE)
        
        manual_btn_x = screen_width//2-8
        manual_btn_y = screen_height//2+16
        pyxel.text(manual_btn_x, manual_btn_y, "RULE", pyxel.COLOR_WHITE)
       
        reset_btn_x = screen_width//2-80
        reset_btn_y = screen_height//2+50
        pyxel.rect(reset_btn_x, reset_btn_y, 10, 10, pyxel.COLOR_RED)
        pyxel.text(reset_btn_x+2, reset_btn_y+2, "RE", pyxel.COLOR_WHITE)

        
        if self.reset_message_timer > 0:
            pyxel.text(screen_width//2+20, screen_height//2-60, "reset completed", pyxel.COLOR_CYAN)

    def draw_manual_scene(self):
        
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        pyxel.rectb(0, 0, screen_width, screen_height, pyxel.COLOR_WHITE)
        pyxel.text(30, 10, "■ゲームの説明", pyxel.COLOR_YELLOW, self.jp_font)
        pyxel.text(30, 30, "←石をよけてスコアを稼ごう", pyxel.COLOR_WHITE, self.jp_font)
        pyxel.text(30, 45, "←アイテムで+100点", pyxel.COLOR_WHITE, self.jp_font)
        pyxel.text(30, 60, "←ハートで残基UP", pyxel.COLOR_WHITE,  self.jp_font)
        pyxel.text(8, 80, "矢印キー[←][→]で操作してね", pyxel.COLOR_WHITE, self.jp_font)
        pyxel.text(40, 100, "クリックで戻る", pyxel.COLOR_RED, self.jp_font)
        
        pyxel.blt(15 , 31, 0, 8, 0, 8, 8, pyxel.COLOR_BLACK)
        pyxel.blt(15 , 46, 0, 32, 0, 8, 8, pyxel.COLOR_BLACK)
        pyxel.blt(15 , 61, 0, 40, 0, 8, 8, pyxel.COLOR_BLACK)

    def draw_ranking_scene(self):
        pyxel.cls(pyxel.COLOR_NAVY)
        pyxel.text(screen_width//2-25, 20, "SCORE RANKING", pyxel.COLOR_YELLOW)
        for i, score in enumerate(self.ranking[:3]):
            pyxel.text(screen_width//2-20, 40+20*i, f"{i+1} : {score}点", pyxel.COLOR_WHITE)
            
            if self.new_rank_index == i:
                pyxel.text(screen_width//2+20, 40+20*i, "NEW!!", pyxel.COLOR_RED)
        pyxel.text(25, 100, "クリックでスタート画面へ", pyxel.COLOR_CYAN, self.jp_font)

    def draw_play_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        for stone in self.stones:
            stone.draw()
        
        if self.item is not None:
            self.item.draw()
        if self.heart_item is not None:
            self.heart_item.draw()
        
        pyxel.blt(self.player_x, self.player_y, 0, 16, 0, 16, 16, pyxel.COLOR_BLACK)
        
        pyxel.text(5, 5, f"Score: {self.score}", pyxel.COLOR_WHITE)
        
        if self.item_get_timer > 0:
            pyxel.text(50, 5, "+100", pyxel.COLOR_YELLOW)
        
        for i in range(self.life):
            pyxel.blt(screen_width-12-10*i, 5, 0, 40, 0, 8, 8, pyxel.COLOR_BLACK)  
        if self.is_collision:
            pyxel.text(screen_width//2-25, screen_height//2-10, "GAME OVER", pyxel.COLOR_RED, self.jp_font)

    def draw(self):
        pyxel.cls(0)
        pyxel.text(10, 10, f"scene: {self.current_scene}", 7)
        if self.current_scene == START_SCENE:
            self.draw_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.draw_play_scene()
        elif self.current_scene == RANKING_SCENE:
            self.draw_ranking_scene()
        elif self.current_scene == MANUAL_SCENE:
            self.draw_manual_scene()

App()
