import pgzrun
from pygame import Rect



WIDTH = 1200
HEIGHT = 600
BLOCK = 32
BASELINE = 564


# ---------- BUTTON CLASS ----------
class Button:
    def __init__(self, text, pos, width=300, height=60):
        self.text = text
        self.rect = Rect((pos[0] - width // 2, pos[1] - height // 2), (width, height))
        self.hovered = False

    def draw(self):
        color = (120, 180, 255) if self.hovered else (60, 120, 200)
        screen.draw.filled_rect(self.rect, color)
        screen.draw.rect(self.rect, "white")
        screen.draw.text(self.text, center=self.rect.center, fontsize=40, color="white")

    def update(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


# ---------- BASE ACTORS ----------
class Ground(Actor):
    def draw(self):
        for x in range(0, WIDTH, self.width):
            screen.blit("ground", (x, BASELINE))


class Platform(Actor):
    def __init__(self):
        super().__init__("platform")
        self.platform_rects = []
        self.platform_positions = []

    def draw(self):
        self.platform_rects.clear()
        self.platform_positions.clear()
        rows = [
            (range(BLOCK * 2, BLOCK * 5, self.width), BASELINE - 64),
            (range(BLOCK * 7, BLOCK * 10, self.width), BASELINE - 128),
            (range(BLOCK * 12, BLOCK * 15, self.width), BASELINE - 192),
            (range(BLOCK * 17, BLOCK * 21, self.width), BASELINE - 256),
            (range(BLOCK * 22, BLOCK * 25, self.width), BASELINE - 320),
            (range(BLOCK * 26, BLOCK * 29, self.width), BASELINE - 384),
            (range(BLOCK * 16, BLOCK * 20, self.width), BASELINE - 384),
            (range(BLOCK * 11, BLOCK * 14, self.width), BASELINE - 448),
            (range(BLOCK * 3, BLOCK * 9, self.width), BASELINE - 512)
        ]
        for row_range, y in rows:
            left_edge = None
            right_edge = None
            for x in row_range:
                screen.blit("platform", (x, y))
                self.platform_rects.append(Rect((x, y), (self.width, self.height)))
                if left_edge is None:
                    left_edge = x
                right_edge = x + self.width
            self.platform_positions.append((left_edge, right_edge, y))


# ---------- COIN ----------
class Coin(Actor):
    def __init__(self, pos):
        super().__init__("coin", pos)
        self.images = ["coin", "coin_side"]
        self.current = 0
        self.timer = 0
        self.speed = 0.15
        self.collected = False

    def update(self):
        if not self.collected:
            self.timer += self.speed
            if self.timer >= 1:
                self.timer = 0
                self.current = (self.current + 1) % len(self.images)
                self.image = self.images[self.current]

    def draw(self):
        if not self.collected:
            super().draw()


# ---------- ENEMY BASE ----------
class EnemyBase(Actor):
    def __init__(self, image, pos):
        super().__init__(image, pos)
        self.alive = True
        self.active = False
        self.frame = 0
        self.timer = 0
        self.anim_speed = 0.2
        self.current_images = []

    def animate(self):
        self.timer += self.anim_speed
        if self.timer >= 1:
            self.timer = 0
            self.frame = (self.frame + 1) % len(self.current_images)
            self.image = self.current_images[self.frame]

    def draw(self):
        if self.alive:
            super().draw()


# ---------- ENEMY ----------
class Enemy(EnemyBase):
    def __init__(self, patrol_range):
        x1, x2, y = patrol_range
        super().__init__("enemy_red_idle_1", (x1 + 16, y - 16))
        self.idle_images = ["enemy_red_idle_1", "enemy_red_idle_2"]
        self.walk_images = ["enemy_red_walk_1", "enemy_red_walk_2"]
        self.walk_left_images = ["enemy_red_walk_left_1", "enemy_red_walk_left_2"]
        self.left_limit = x1 + 8
        self.right_limit = x2 - 8
        self.direction = 1
        self.speed = 2
        self.current_images = self.idle_images

    def update(self, player_started):
        if not self.alive:
            return
        if player_started and not self.active:
            self.active = True
            self.current_images = self.walk_images
        if self.active:
            self.x += self.speed * self.direction
            if self.x <= self.left_limit:
                self.direction = 1
                self.current_images = self.walk_images
            elif self.x >= self.right_limit:
                self.direction = -1
                self.current_images = self.walk_left_images
        self.animate()


# ---------- ENEMY BAT----------
class EnemyBat(EnemyBase):
    def __init__(self, patrol_range):
        x1, x2, y = patrol_range
        start_x = int((x1 + x2) / 2)
        start_y = int(y - 40)
        super().__init__("enemy_bat_idle_1", (start_x, start_y))
        self.idle_images = ["enemy_bat_idle_1", "enemy_bat_idle_2"]
        self.fly_images = [f"enemy_bat_fly_{i}" for i in range(1, 7)]
        self.fly_left_images = [f"enemy_bat_fly_left_{i}" for i in range(1, 7)]
        self.left_limit = x1
        self.right_limit = x2
        self.top_limit = max(0, y - 200)
        self.bottom_limit = max(self.top_limit + 40, y - 32)
        self.direction_x = 1
        self.direction_y = 1
        self.speed_x = 2
        self.speed_y = 1
        self.current_images = self.idle_images

    def update(self, player_started):
        if not self.alive:
            return
        if player_started and not self.active:
            self.active = True
            self.current_images = self.fly_images
        if self.active:
            self.x += self.speed_x * self.direction_x
            self.y += self.speed_y * self.direction_y
            if self.x <= self.left_limit:
                self.direction_x = 1
                self.current_images = self.fly_images
            elif self.x >= self.right_limit:
                self.direction_x = -1
                self.current_images = self.fly_left_images
            if self.y <= self.top_limit:
                self.direction_y = 1
            elif self.y >= self.bottom_limit:
                self.direction_y = -1
        self.animate()


# ---------- PLAYER ----------
class Player(Actor):
    def __init__(self, pos):
        super().__init__("player_idle_1", pos)
        self.idle_images = ["player_idle_1", "player_idle_2", "player_idle_3", "player_idle_4"]
        self.walk_images = ["player_walk_1", "player_walk_2", "player_walk_3",
                            "player_walk_4", "player_walk_5", "player_walk_6"]
        self.walk_left_images = ["player_walk_left_1", "player_walk_left_2", "player_walk_left_3",
                                 "player_walk_left_4", "player_walk_left_5", "player_walk_left_6"]
        self.jump_images = ["player_jump_1", "player_jump_2", "player_jump_3",
                            "player_jump_4", "player_jump_5", "player_jump_6",
                            "player_jump_7", "player_jump_8"]
        self.hurt_images = ["player_hurt_1", "player_hurt_2", "player_hurt_3", "player_hurt_4"]
        self.current_images = self.idle_images
        self.frame = 0
        self.timer = 0
        self.anim_speed = 0.15
        self.speed = 4
        self.vx = 0
        self.vy = 0
        self.gravity = 0.5
        self.jump_strength = 10
        self.on_ground = True
        self.facing_right = True
        self.coins_collected = 0
        self.lives = 3
        self.invincible_timer = 0
        self.hurt = False

    def handle_input(self):
        if keyboard.left:
            self.vx = -self.speed
            self.current_images = self.walk_left_images
            self.facing_right = False
        elif keyboard.right:
            self.vx = self.speed
            self.current_images = self.walk_images
            self.facing_right = True
        else:
            self.vx = 0
            if self.on_ground and not self.hurt:
                self.current_images = self.idle_images
        if keyboard.space and self.on_ground:
            self.vy = -self.jump_strength
            self.on_ground = False
            self.current_images = self.jump_images
            self.frame = 0
            self.timer = 0

    def apply_gravity(self):
        self.vy += self.gravity
        self.y += self.vy
        self.x += self.vx
        if self.y >= BASELINE - 16:
            self.y = BASELINE - 16
            self.vy = 0
            self.on_ground = True
        self.x = max(0, min(WIDTH, self.x))

    def check_platforms(self, platform_rects):
        self_rect = Rect((self.x - self.width / 2, self.y - self.height / 2),
                         (self.width, self.height))
        landed = False
        for rect in platform_rects:
            if self.vy >= 0 and self_rect.colliderect(rect):
                if self_rect.bottom - self.vy <= rect.top:
                    self.y = rect.top - self.height / 2
                    self.vy = 0
                    self.on_ground = True
                    landed = True
                    break
        if not landed and self.y < BASELINE - 32:
            self.on_ground = False

    def check_coins(self, coins, sound_on):
        player_rect = Rect((self.x - self.width / 2, self.y - self.height / 2),
                           (self.width, self.height))
        for c in coins:
            if not c.collected:
                coin_rect = Rect((c.x - c.width / 2, c.y - c.height / 2),
                                 (c.width, c.height))
                if player_rect.colliderect(coin_rect):
                    c.collected = True
                    self.coins_collected += 1
                    if sound_on:
                        sounds.coin_collect.play()

    def check_enemies(self, enemies, sound_on):
        player_rect = Rect((self.x - self.width / 2, self.y - self.height / 2),
                           (self.width, self.height))
        for e in enemies:
            if not e.alive:
                continue
            enemy_rect = Rect((e.x - e.width / 2, e.y - e.height / 2),
                              (e.width, e.height))
            if player_rect.colliderect(enemy_rect):
                if self.vy > 0 and self.y < e.y:
                    e.alive = False
                    if sound_on:
                        sounds.killed.play()
                    self.vy = -8
                elif self.invincible_timer == 0:
                    self.take_damage(sound_on)

    def take_damage(self, sound_on):
        self.lives -= 1
        self.hurt = True
        self.invincible_timer = 90
        self.current_images = self.hurt_images
        self.frame = 0
        self.timer = 0
        if sound_on:
            sounds.hurt.play()

    def animate(self):
        self.timer += self.anim_speed
        if self.timer >= 1:
            self.timer = 0
            self.frame = (self.frame + 1) % len(self.current_images)
            self.image = self.current_images[self.frame]

    def update(self, platform_rects, coins, enemies, sound_on):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer == 0:
                self.hurt = False
        self.handle_input()
        self.apply_gravity()
        self.check_platforms(platform_rects)
        self.check_coins(coins, sound_on)
        self.check_enemies(enemies, sound_on)
        self.animate()


# ---------- TORCH ----------
class Torch(Actor):
    def __init__(self):
        super().__init__("torch_off", (WIDTH - 50, BASELINE - 16))
        self.images = ["torch_on_a", "torch_on_b"]
        self.current = 0
        self.timer = 0
        self.speed = 0.2
        self.lit = False

    def update(self):
        if self.lit:
            self.timer += self.speed
            if self.timer >= 1:
                self.timer = 0
                self.current = (self.current + 1) % len(self.images)
                self.image = self.images[self.current]
        else:
            self.image = "torch_off"


# ---------- GAME CLASS ----------
class Game:
    def __init__(self):
        self.state = "menu"
        self.music_on = True
        self.sound_on = True
        self.end_message = ""
        self.mouse_pos = (0, 0)
        self.player_started = False

        self.ground = Ground("ground")
        self.platforms = Platform()
        self.player = Player((BLOCK, BASELINE - 16))
        self.torch = Torch()

        self.coins = [
            Coin((BLOCK * 3 + 16, BASELINE - 96)),
            Coin((BLOCK * 8 + 16, BASELINE - 160)),
            Coin((BLOCK * 13 + 16, BASELINE - 224)),
            Coin((BLOCK * 18 + 16, BASELINE - 288)),
            Coin((BLOCK * 23 + 16, BASELINE - 352)),
            Coin((BLOCK * 27 + 16, BASELINE - 416)),
            Coin((BLOCK * 17 + 16, BASELINE - 416)),
            Coin((BLOCK * 12 + 16, BASELINE - 480)),
            Coin((BLOCK * 5 + 16, BASELINE - 544))
        ]

        self.enemies = []
        self.bats = []
        self.create_enemies()

        # menu buttons
        self.start_btn = Button("Start Game", (WIDTH // 2, 250))
        self.music_btn = Button("Music: ON", (WIDTH // 2, 330))
        self.sound_btn = Button("Sound: ON", (WIDTH // 2, 410))
        self.exit_btn = Button("Exit Game", (WIDTH // 2, 490))

        music.play('background_music')

    def create_enemies(self):
        for p in self.platforms.platform_positions[:5]:
            self.enemies.append(Enemy(p))
        for p in self.platforms.platform_positions[5:9]:
            self.bats.append(EnemyBat(p))

    def update(self):
        if self.state == "menu":
            self.start_btn.update(self.mouse_pos)
            self.music_btn.update(self.mouse_pos)
            self.sound_btn.update(self.mouse_pos)
            self.exit_btn.update(self.mouse_pos)
        elif self.state == "playing":
            self.update_playing()

    def update_playing(self):
        if not self.enemies and not self.bats:
            self.create_enemies()
        for c in self.coins:
            c.update()
        self.player.update(self.platforms.platform_rects, self.coins, self.enemies + self.bats, self.sound_on)
        for e in self.enemies + self.bats:
            e.update(self.player_started)
        self.torch.update()
        if keyboard.left or keyboard.right:
            self.player_started = True

        if self.player.lives <= 0:
            self.end_game("Game Over")
        if all(c.collected for c in self.coins):
            self.torch.lit = True
        if self.torch.lit:
            player_rect = Rect((self.player.x - self.player.width / 2, self.player.y - self.player.height / 2),
                               (self.player.width, self.player.height))
            torch_rect = Rect((self.torch.x - self.torch.width / 2, self.torch.y - self.torch.height / 2),
                               (self.torch.width, self.torch.height))
            if player_rect.colliderect(torch_rect):
                self.end_game("Victory!")

    def draw(self):
        screen.fill("white")
        for x in range(0, WIDTH, 256):
            screen.blit("background_clouds", (x, 0))
        for x in range(0, WIDTH, 256):
            screen.blit("background_color_trees", (x, 310))

        if self.state == "menu":
            screen.draw.text("KENAN'S PLATFORMER", center=(WIDTH // 2, 130), fontsize=70, color="white", shadow=(2, 2))
            for btn in [self.start_btn, self.music_btn, self.sound_btn, self.exit_btn]:
                btn.draw()

        elif self.state == "playing":
            self.ground.draw()
            self.platforms.draw()
            for c in self.coins:
                c.draw()
            for e in self.enemies + self.bats:
                e.draw()
            self.player.draw()
            self.torch.draw()
            self.draw_hud()

        elif self.state == "end":
            screen.fill((0, 0, 0))
            screen.draw.text(self.end_message, center=(WIDTH // 2, HEIGHT // 2 - 50),
                             fontsize=90,
                             color="yellow" if self.end_message == "Victory!" else "red",
                             shadow=(2, 2))
            screen.draw.text("Click to return to menu", center=(WIDTH // 2, HEIGHT // 2 + 50),
                             fontsize=40, color="white")

    def draw_hud(self):
        screen.draw.text(f"Coins: {self.player.coins_collected}/{len(self.coins)}",
                         (1000, 20), fontsize=40, color="yellow", shadow=(1, 1))
        for i in range(3):
            heart = "heart" if i < self.player.lives else "heart_empty"
            screen.blit(heart, (1000 + i * 40, 70))

    def end_game(self, message):
        self.end_message = message
        self.state = "end"
        music.stop()
        music.play('end_music')

    def reset_game(self):
        self.__init__()

    def mouse_move(self, pos):
        self.mouse_pos = pos

    def mouse_down(self, pos):
        if self.state == "menu":
            if self.start_btn.clicked(pos):
                self.state = "playing"
                if self.music_on:
                    music.play('background_music')
            elif self.music_btn.clicked(pos):
                self.music_on = not self.music_on
                self.music_btn.text = f"Music: {'ON' if self.music_on else 'OFF'}"
                if self.music_on:
                    music.play('background_music')
                else:
                    music.stop()
            elif self.sound_btn.clicked(pos):
                self.sound_on = not self.sound_on
                self.sound_btn.text = f"Sound: {'ON' if self.sound_on else 'OFF'}"
            elif self.exit_btn.clicked(pos):
                exit()
        elif self.state == "end":
            self.reset_game()


# ---------- MAIN EXECUTION ----------
game = Game()


def update():
    game.update()


def draw():
    game.draw()


def on_mouse_move(pos):
    game.mouse_move(pos)


def on_mouse_down(pos):
    game.mouse_down(pos)


pgzrun.go()
