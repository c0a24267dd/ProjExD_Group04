import random
import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
# --- 1. Card Class ---
class Card:
    """カードの基本情報"""
    def __init__(self, id, name, attack, cost, img,type,power):
        self.id = id
        self.name = name
        self.attack = attack        # アタック値
        self.cost = cost     # マナコスト 
        self.power = power # パワー
        self.img = img # 画像名
        self.type = type # カードタイプ

              
        # 実際にはテキストや効果も持つ
# --- 2. Creature Class ---
class Creature:
    """場に出ているクリーチャーの状態"""
    def __init__(self, card):
        self.card = card
        self.current_attack = card.attack # 現状は固定だが、効果で変わる可能性を考慮
        self.current_power = card.power
        self.is_tapped = False
        self.can_attack_this_turn = False # 出たターンはアタック不可

# --- 3. Player Class ---
class Player:
    """プレイヤーの基本情報と所有物を管理"""
    def __init__(self, is_player1=True):
        self.is_player1 = is_player1
        self.life = 10
        self.deck = []
        self.hand = []
        self.graveyard = [] #  墓地
        self.mana = 0
        self.max_mana = 0
        self.field = [] # 場に出ているCreatureオブジェクトのリスト

    def draw_card(self):
        """山札からカードを引く"""
        if not self.deck:
            # 山札切れによる敗北判定
            return False 
        card = self.deck.pop(0)
        self.hand.append(card)
        return True

    def setup_deck(self, card_list):
        """デッキを初期化してシャッフル"""
        # 5種4枚の合計20枚をセットアップ
        self.deck = card_list * 4 
        random.shuffle(self.deck)

    def select(self,opponent_player):
        selected_card = None
        while(selected_card == None):
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if self.is_player1:
                        for i, card in enumerate(opponent_player.field):
                            rect = pygame.Rect(200 + i * 110, 220, 100, 140)
                            if rect.collidepoint(pos):
                                selected_card = card
                    else:
                        for i, card in enumerate(opponent_player.field):
                            rect = pygame.Rect(200 + i * 110, SCREEN_HEIGHT - 350, 100, 140)
                            if rect.collidepoint(pos):
                                selected_card = card
        return selected_card


# --- 4. Game Class ---
class Game:
    """ゲーム全体の進行と状態を管理"""
    def __init__(self):
        # カード定義の例 (実際のゲームではより複雑)
        CARD_PROTOTYPES = [
            Card(1, "こうかーん", 7, 6,"fig/こうかーん.jpg","C",6000),  # id,name,attack,cost,img,type
            Card(2, "ボーグとん", 1, 2,"fig/ボーグとん.jpg","C",2000),
            Card(3, "ハルカとん", 1, 3,"fig/ハルカとん.png","C",3000),
            Card(4, "アルカとん",2, 5,"fig/アルカとん.jpg","C",2000),
            Card(5,"鳥鍋祭り",0,4,"fig/鳥鍋こうかとん.png","M",0),
        ]
        
        self.player1 = Player(is_player1=True)
        self.player2 = Player(is_player1=False)
        
        self.player1.setup_deck(CARD_PROTOTYPES)
        self.player2.setup_deck(CARD_PROTOTYPES) # デッキは同じ定義でOK
        
        # 先攻後攻をランダムで決定
        self.current_turn_player = random.choice([self.player1, self.player2])
        self.turn_count = 1
        self.game_state = 'START'
        self.current_turn_player.max_mana = min(self.current_turn_player.max_mana + 1, 10)
        self.current_turn_player.mana = self.current_turn_player.max_mana
        self.current_turn_player.go = "先攻"
        if self.current_turn_player == self.player1:
            self.player2.go = "後攻"
        else:
            self.player1.go = "後攻"
        self.init_game()

    def init_game(self):
        """ゲーム開始時の初期設定"""
        for _ in range(3):
            self.player1.draw_card()
            self.player2.draw_card()
        self.game_state = 'MAIN_PHASE'

    def next_turn(self):
        """ターン進行処理"""
        # プレイヤーの交代
        if self.current_turn_player == self.player1:
            self.current_turn_player = self.player2
            self.turn_count += 1
            for c in self.player2.field:
                c.is_tapped = False
                c.can_attack_this_turn = True
        else:
            self.current_turn_player = self.player1
            self.turn_count += 1
            for c in self.player1.field:
                c.is_tapped = False
                c.can_attack_this_turn = True
            
        player = self.current_turn_player
        
        # マナの増加
        player.max_mana = min(player.max_mana + 1, 10) # 例として最大マナを10に設定
        player.mana = player.max_mana
        
        # クリーチャーのフラグ更新
        for creature in player.field:
            creature.is_tapped = False
            creature.can_attack_this_turn = True 

        # ドロー (先攻1ターン目以外)
        if self.turn_count >= 1 or (self.turn_count == 1 and self.current_turn_player == self.player2):
            if not player.draw_card():
                # ドロー失敗で山札切れ負け
                if player == self.player1:
                    return "Player 2 Win (Deck Out)"
                else:
                    return "Player 1 Win (Deck Out)"
        
        self.game_state = 'MAIN_PHASE'
        return self.check_win_condition()

    def check_win_condition(self):
        """勝利条件のチェック"""
        if self.player1.life <= 0: # 山札切れ敗北の機能追加が必要
            return "Player 2 Win"
        if self.player2.life <= 0:
            return "Player 1 Win"
        # 実際にはドロー時の山札切れチェックも必要
        return None
    
class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 60)
        self.font_small = pygame.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return  # クリックされたら抜けてゲーム開始

            self.screen.fill((0,0,0))
            title = self.font_big.render("Kokaton Master's", True, (255,255,255))
            msg = self.font_small.render("Click to Start", True, (255,255,255))
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2 + 50))

            pygame.display.flip()

class ResultScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 60)
        self.font_small = pygame.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)

    def run(self, result_message):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return # クリックでリザルト画面を終了
            self.screen.fill((0,0,0))
            title = self.font_big.render("Game End", True, (255,255,255))
            msg = self.font_small.render(result_message, True, (255,255,255))
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2 + 50))                
                    
            pygame.display.flip()
def battle(attacker, enemy, attack_player, def_player):  # 追加機能４
    """
    バトルの処理をする関数
    選択された両プレイヤーのクリーチャーをバトルさせる関数
    引数 attacker = 攻撃側のカード, enemy = 攻撃された側のカード, attack_player = ターンプレイヤー, def_player = もう一人のプレイヤー
    """
    if not attacker or not enemy:  # 両変数にカードが格納されているか確認する
        return

    print("=== Battle Start ===")

    if enemy.current_power < attacker.current_power:  # 防御側が負けの場合
        for n in def_player.field:  # 防御側のフィールドリストにカードが存在するか調べる
            if n is enemy:
                def_player.field.remove(n)  # フィールドから負けたカードを削除する
                def_player.graveyard.append(n)  # 墓地に負けたカードを追加する
                break
        else:
            print("※ enemy が field に見つかりません（参照ずれ）")
    elif attacker.current_power < enemy.current_power:  # 攻撃側が負けの場合
        for n in attack_player.field:  # 攻撃側のフィールドリストにカードが存在するか調べる
            if n is attacker:
                attack_player.field.remove(n)  # フィールドから負けたカードを削除する
                attack_player.graveyard.append(n)  # 墓地に負けたカードを追加する
                break
    else:  # 相打ちの場合
        for n in def_player.field:  # 防御側のフィールドリストにカードが存在するか調べる
            if n is enemy:
                def_player.field.remove(n)  # フィールドから負けたカードを削除する
                def_player.graveyard.append(n)  # 墓地に負けたカードを追加する
                break
        for n in attack_player.field:  # 攻撃側のフィールドリストにカードが存在するか調べる
            if n is attacker:
                attack_player.field.remove(n)  # フィールドから負けたカードを削除する
                attack_player.graveyard.append(n)  # 墓地に負けたカードを追加する
                break
    print("=== Battle End ===")
    return

def attack_creature(num, attack_card, attack_player):  # 追加機能４
    """
    攻撃に関するクラス
    攻撃選択したクリーチャーがフィールドに存在するか調べる。
    引数 num = リストの順番, attack_card = 攻撃側のカード, attack_player = 攻撃側のプレイヤー
    """
    if attack_card is None:  # 攻撃するカードが選択されているか調べる
        attack_card = attack_player.field[num]  # 選択したカードを対応するプレイヤーのフィールドリストから取り出し格納する
        print(f"攻撃側選択: {attack_card.card.name}")
    elif attack_card == attack_player.field[num]:  # 攻撃側をもう一度クリックすると選択解除
        print(f"攻撃側解除: {attack_card.card.name}")
        attack_card = None
    return attack_card  # 攻撃するカードの変数を返す

def chosen_creature(num, enemy_card, enemy_player):  # 追加機能４
    """
    攻撃先選択に関するクラス
    攻撃先に選択したクリーチャーがフィールドに存在するか調べる。
    引数 num = リストの順番, enemy_card = 選択されたカード, enemy_player = 攻撃を受ける側のプレイヤー
    """
    if enemy_player is not None:  # enemy_cardの中身が存在するか調べる
        enemy_card = enemy_player.field[num]  # 選択したカードを対応するプレイヤーのフィールドリストから取り出す
        if enemy_card.is_tapped:  # 選ばれたカードがタップされているか確認する
            print(f"防御側選択: {enemy_card.card.name}")
        else:  # タップされていなければ選択を無効にする
            enemy_card = None
    elif enemy_card == enemy_player.field[num]:  # 攻撃側をもう一度クリックすると選択解除
        print(f"防御側解除: {enemy_card.card.name}")
        enemy_card = None
    return enemy_card  # 選ばれたカードを返す

import pygame
import sys
# Gameクラス、Playerクラスなどは上記で定義済みとする

# --- Pygameの初期設定 ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Kokaton Master's")

# 定数
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
GREEN = (100,200,100)
YELLOW = (150,150,50)
FONT = pygame.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 20)
FONT_FLAME = pygame.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 21)

#BGMファイル名
BGM_NORMAL = "Noesis.mp3"
BGM_CRISIS = "予告.mp3"
current_bgm_state = 'NONE'
    
def start_bgm(file_path):
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play(-1)   

# --- 描画ユーティリティ関数 ---
def draw_card_on_screen(screen, card_obj, x, y, is_creature=False, is_tapped=False):
    """カードを画面に描画する（簡略化された四角形）"""
    card_rect = pygame.Rect(x, y, 100, 140)

    
    # 基本の描画
    if is_creature:
        if card_obj.card.id == 1 or card_obj.card.id == 2 or card_obj.card.id == 4:
            img = pygame.image.load(card_obj.card.img)
            img = pygame.transform.rotozoom(img,0,0.2)
            screen.blit(img,card_rect)
        else:
            img = pygame.image.load(card_obj.card.img)
            img = pygame.transform.rotozoom(img,0,0.25)
            screen.blit(img,card_rect)
    else:
        if(card_obj.id == 1 or card_obj.id == 2 or card_obj.id == 4):
            img = pygame.image.load(card_obj.img)
            img = pygame.transform.rotozoom(img,0,0.2)
            screen.blit(img,card_rect)
        else:
            img = pygame.image.load(card_obj.img)
            img = pygame.transform.rotozoom(img,0,0.25)
            screen.blit(img,card_rect)
    if is_tapped:
        color = (150, 150, 150) # タップしている場合は灰色に
        tap_img = pygame.Surface((100,140))
        pygame.draw.rect(tap_img, color,pygame.Rect(0,0,100,140))
        tap_img.set_alpha(160)
        screen.blit(tap_img, card_rect)
    # 情報の描画
    name_surf = FONT.render(card_obj.card.name if is_creature else card_obj.name, True, WHITE)
    name_flame = FONT_FLAME.render(card_obj.card.name if is_creature else card_obj.name, True, BLACK)
    attack_surf = FONT.render(f"A:{card_obj.card.attack if is_creature else card_obj.attack}", True, WHITE)
    attack_flame = FONT_FLAME.render(f"A:{card_obj.card.attack if is_creature else card_obj.attack}", True, BLACK)
    cost_surf = FONT.render(f"C:{card_obj.card.cost if is_creature else card_obj.cost}", True, WHITE)
    cost_flame = FONT_FLAME.render(f"C:{card_obj.card.cost if is_creature else card_obj.cost}", True, BLACK)
    power_surf = FONT.render(f"P:{card_obj.card.power if is_creature else card_obj.power}", True, WHITE)
    power_flame = FONT_FLAME.render(f"P:{card_obj.card.power if is_creature else card_obj.power}", True, BLACK)

    screen.blit(name_flame, (x + 5, y + 50))
    screen.blit(name_surf, (x + 5, y + 50))
    screen.blit(attack_flame, (x + 70, y + 110))
    screen.blit(attack_surf, (x + 70, y + 110))
    screen.blit(cost_flame, (x + 5, y + 5))
    screen.blit(cost_surf, (x + 5, y + 5))
    screen.blit(power_flame, (x + 5, y + 110))
    screen.blit(power_surf, (x + 5, y + 110))

    return card_rect # クリック判定用にRectを返す

def draw_player_status(screen, player, x, y,current):
    """ライフとマナと先攻後攻の表示"""
    if player.is_player1:
        player_text = FONT.render(f"name:{"player1"}", True, WHITE)
    else:
        player_text = FONT.render(f"name:{"player2"}", True, WHITE)
    deck_text = FONT.render(f"Deck: {len(player.deck)}", True, WHITE)
    life_text = FONT.render(f"LIFE: {player.life}", True, WHITE)
    mana_text = FONT.render(f"MANA: {player.mana}/{player.max_mana}", True, WHITE)
    if player == current:
        go_text = FONT.render(player.go, True, RED)
    else:
        go_text = FONT.render(player.go, True, WHITE)

    screen.blit(player_text, (x, y - 30))
    screen.blit(deck_text, (x, y))
    screen.blit(life_text, (x, y + 30))
    screen.blit(mana_text, (x, y + 60))
    screen.blit(go_text, (x, y + 90))
# --- メインゲームループ ---
def run_game():
    game = Game()
    running = True
    
    # 選択中のカード/クリーチャーを管理する変数
    selected_card = None
    attack_card = None
    enemy_card = None
    target_card = None
    result = None
    
    #BGMの再生
    try:
        start_bgm(BGM_NORMAL)
        current_bgm_state = 'NORMAL'
    except pygame.error as e:
        print(f"BGMファイルのロードに失敗しました: {e}. {BGM_NORMAL}が存在するか確認してください。")
        current_bgm_state = 'NONE'
    
    while running:
        current_player = game.current_turn_player
        opponent_player = game.player2 if current_player == game.player1 else game.player1
        if current_bgm_state != 'NONE':
            player1_life = game.player1.life 
            
            if player1_life <= 3 and current_bgm_state == 'NORMAL':
                try:
                    start_bgm(BGM_CRISIS)
                    current_bgm_state = 'CRISIS'
                except pygame.error as e:
                    print(f"BGMファイルのロードに失敗しました: {e}. {BGM_CRISIS}が存在するか確認してください。")
                    current_bgm_state = 'NONE' 
            elif player1_life > 3 and current_bgm_state == 'CRISIS':
                try:
                    start_bgm(BGM_NORMAL)
                    current_bgm_state = 'NORMAL'
                except pygame.error as e:
                    print(f"BGMファイルのロードに失敗しました: {e}. {BGM_NORMAL}が存在するか確認してください。")
                    current_bgm_state = 'NONE'
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                result = "Quit" # 終了理由を設定

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                
                # --- ターン終了ボタンのクリック判定 ---
                end_turn_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - 25, 120, 50)
                if end_turn_rect.collidepoint(pos):
                    result = game.next_turn()
                    game.game_state = 'MAIN_PHASE'
                    if result:
                        running = False

                # --- カード使用ボタンの判定 ---
                if game.game_state == 'MAIN_PHASE':
                    use_card_rect = pygame.Rect(30, SCREEN_HEIGHT // 2 - 25, 120, 50)
                    if use_card_rect.collidepoint(pos):
                        if(selected_card != None):
                            if(selected_card.cost <= current_player.mana):
                                if(selected_card.type == "C"):
                                    current_player.mana -= selected_card.cost
                                    current_player.field.append(Creature(selected_card))
                                    current_player.hand.remove(selected_card)
                                    if(selected_card.id == 4): #  id4番目は相手のクリーチャーを1体選び破壊
                                        target_card = current_player.select(opponent_player)
                                        opponent_player.field.remove(target_card)
                                        opponent_player.graveyard.append(target_card)
                                        target_card = None
                                    if(selected_card.id == 3):
                                        current_player.draw_card()
                                    selected_card = None
                                elif(selected_card.type == "M"): # カードが呪文の場合
                                    if(selected_card.id == 5): # idが6の処理(今回のカードの処理)
                                        current_player.mana -= selected_card.cost
                                        if(opponent_player.field != []):
                                            target_card = current_player.select(opponent_player)
                                            opponent_player.field.remove(target_card)
                                            opponent_player.graveyard.append(target_card)
                                        current_player.draw_card()
                                        current_player.hand.remove(selected_card)
                                        current_player.graveyard.append(selected_card)
                                        selected_card = None
                                        target_card = None
                    # --- カードを選ぶ判定 ---
                    if current_player == game.player1:
                        for i, card in enumerate(current_player.hand):
                            if pygame.Rect(200 + i * 110, SCREEN_HEIGHT - 170, 300 + i * 110, SCREEN_HEIGHT - 30).collidepoint(pos):
                                selected_card = card
                    else:
                        for i, card in enumerate(current_player.hand):
                            if pygame.Rect(200 + i * 110, 30, 300 + i * 110, 170).collidepoint(pos):
                                selected_card = card
                # --- 攻撃の実装 --- 追加機能４
                if current_player == game.player1:  # 攻撃するプレイヤーがプレイヤー1か2かを特定する
                    for i, card in enumerate(current_player.field):  # 自分のカードを選択、フィールド関数に存在するカードを取り出す
                        rect = pygame.Rect(200 + i * 110, SCREEN_HEIGHT - 350, 100, 140)  # フィールド上のカードの位置を格納する
                        if rect.collidepoint(pos):  # blitされているカードが押されたかを確認
                            attack_card = attack_creature(i, attack_card, current_player)  # 攻撃カード選択関数を呼び出す
                    for i, card in enumerate(opponent_player.field):  # 相手のカードを選択、フィールド関数に存在するカードを取り出す
                        rect = pygame.Rect(200 + i * 110, 220, 100, 140)  # フィールド上のカードの位置を格納する
                        if rect.collidepoint(pos):  # blitされているカードが押されたかを確認
                            enemy_card = chosen_creature(i, enemy_card, opponent_player)  # 攻撃先カード選択関数を呼び出す
                else:  # 上と同様に攻撃プレイヤーが逆だった場合を調べる
                    for i, card in enumerate(current_player.field):
                        rect = pygame.Rect(200 + i * 110, 220, 100, 140)
                        if rect.collidepoint(pos):
                            attack_card = attack_creature(i, attack_card, current_player)
                    for i, card in enumerate(opponent_player.field):
                        rect = pygame.Rect(200 + i * 110, SCREEN_HEIGHT - 350, 100, 140)
                        if rect.collidepoint(pos):
                            enemy_card = chosen_creature(i, enemy_card, opponent_player)
                attack_card_rect = pygame.Rect(30, SCREEN_HEIGHT // 2 - 75, 120, 50)  # 攻撃ボタンの位置を調べる
                if attack_card_rect.collidepoint(pos):  # 攻撃ボタンが押された場合、攻撃へ進む
                        if attack_card is None:  # 攻撃カードが存在しない場合は無効にする
                            continue                        
                        if not attack_card.is_tapped and attack_card.can_attack_this_turn:  # 攻撃カードがタップしていないことと、攻撃可能であることを調べる
                            game.game_state = 'ATTACK_PHASE'  # statusをアタックフェーズに切り替える
                            attack_card.is_tapped = True  # 攻撃するカードをタップする
                            if enemy_card is not None:  # 攻撃先カードが存在するか調べる
                                battle(attack_card, enemy_card, current_player, opponent_player)  # battle関数を呼び出し、処理させる
                            else:
                                opponent_player.life -= attack_card.current_attack  # 攻撃先のカードが選択されていない、もしくは攻撃先のカードが選択されていない場合は相手のライフを攻撃する
                        attack_card = None  # 選んだ各カードの変数を初期化する
                        enemy_card = None

                
        # --- 描画処理 ---
        screen.fill(GREEN)
        
        # プレイヤー1 (下側) の情報表示
        draw_player_status(screen, game.player1, 50, SCREEN_HEIGHT - 150,current_player)
        
        # プレイヤー2 (上側) の情報表示
        draw_player_status(screen, game.player2, 50, 50,current_player)
        
        # 手札の描画 (プレイヤー1: 下)
        for i, card in enumerate(game.player1.hand):
            draw_card_on_screen(screen, card, 200 + i * 110, SCREEN_HEIGHT - 170)
        # 手札の描画 (プレイヤー2: 上)
        for i, card in enumerate(game.player2.hand):
            draw_card_on_screen(screen, card, 200 + i * 110, 30)

        # 場に出ているクリーチャーの描画 (プレイヤー1: 中央下)
        for i, creature in enumerate(game.player1.field):
            draw_card_on_screen(screen, creature, 200 + i * 110, SCREEN_HEIGHT - 350, 
                                is_creature=True, is_tapped=creature.is_tapped)

        # 場に出ているクリーチャーの描画 (プレイヤー2: 中央上)
        for i, creature in enumerate(game.player2.field):
            draw_card_on_screen(screen, creature, 200 + i * 110, 220, 
                                is_creature=True, is_tapped=creature.is_tapped)
        # カード使用ボタン
        use_card_rect = pygame.Rect(30, SCREEN_HEIGHT // 2 - 25, 120, 50)
        pygame.draw.rect(screen, BLUE, use_card_rect, border_radius=5)
        use_text = FONT.render("Use card", True, WHITE)
        screen.blit(use_text, (use_card_rect.x + 10, use_card_rect.y + 15))

        # 攻撃宣言ボタン
        attack_card_rect = pygame.Rect(30, SCREEN_HEIGHT // 2 - 75, 120, 50)
        pygame.draw.rect(screen, YELLOW, attack_card_rect, border_radius=5)
        attack_text = FONT.render("Attack", True, WHITE)
        screen.blit(attack_text, (attack_card_rect.x + 10, attack_card_rect.y + 15))

        # ターン終了ボタン
        end_turn_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - 25, 120, 50)
        pygame.draw.rect(screen, RED, end_turn_rect, border_radius=5)
        end_text = FONT.render("End Turn", True, WHITE)
        screen.blit(end_text, (end_turn_rect.x + 10, end_turn_rect.y + 15))

        pygame.display.flip()
        
        # ループ内での勝利条件チェック (攻撃後のライフ減少に対応)
        if not result:
            result = game.check_win_condition()
            
        if result:
            running = False

    # メインループ終了後、リザルト画面を表示
    if result:
        re = ResultScreen(screen)
        re.run(result)

    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    st = StartScreen(screen)
    st.run()
    run_game()