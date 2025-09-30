import pygame
import sys
import random
import time
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bot Escape - Survival Challenge")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
PINK = (255, 20, 147)

PLAYER_SIZE = 35
BASE_SPEED = 4
BASE_BULLET_SPEED = 6

class PlayerSkin:
    def __init__(self, name, shape, color, unlock_level):
        self.name = name
        self.shape = shape
        self.color = color
        self.unlock_level = unlock_level

AVAILABLE_SKINS = [
    PlayerSkin("Classic", "square", BLUE, 1),
    PlayerSkin("Triangle", "triangle", BLUE, 3),
    PlayerSkin("Circle", "circle", BLUE, 5),
    PlayerSkin("Red Square", "square", RED, 7),
    PlayerSkin("Yellow Triangle", "triangle", YELLOW, 10),
    PlayerSkin("Green Circle", "circle", GREEN, 12),
    PlayerSkin("Cyan Square", "square", CYAN, 15),
    PlayerSkin("Pink Triangle", "triangle", PINK, 18),
    PlayerSkin("Purple Circle", "circle", PURPLE, 20)
]

from gamesave import save_game_progress, load_game_progress

class GameStats:
    def __init__(self):
        self.best_time = 0
        self.best_wave = 1
        self.player_lvl = 1
        self.xp = 0
        self.xp_target = 100
        self.selected_skin = 0
        load_game_progress(self)

class Player:
    def __init__(self, x, y, skin_index=0):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = BASE_SPEED
        self.hp = 100
        self.max_hp = 100
        self.skin = AVAILABLE_SKINS[skin_index]
        
    def move(self, keys):
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed
    
    def draw(self, surface):
        if self.skin.shape == "square":
            pygame.draw.rect(surface, self.skin.color, self.rect)
        elif self.skin.shape == "triangle":
            points = [
                (self.rect.centerx, self.rect.top),
                (self.rect.left, self.rect.bottom),
                (self.rect.right, self.rect.bottom)
            ]
            pygame.draw.polygon(surface, self.skin.color, points)
        elif self.skin.shape == "circle":
            pygame.draw.circle(surface, self.skin.color, self.rect.center, PLAYER_SIZE // 2)
        
        if self.hp < self.max_hp:
            bar_w = 40
            bar_h = 6
            bar_x = self.rect.centerx - bar_w // 2
            bar_y = self.rect.top - 10
            pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_w, bar_h))
            hp_w = int((self.hp / self.max_hp) * bar_w)
            pygame.draw.rect(surface, GREEN, (bar_x, bar_y, hp_w, bar_h))

class Enemy:
    def __init__(self, x, y, enemy_type=0):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.type = enemy_type
        self.last_fire = 0
        self.target_y = y
        self.move_counter = 0
        
        if enemy_type == 0:
            self.color = RED
            self.fire_delay = 2000
            self.aim_spread = 30
            self.move_speed = 1
        elif enemy_type == 1:
            self.color = ORANGE
            self.fire_delay = 1500
            self.aim_spread = 20
            self.move_speed = 1.5
        elif enemy_type == 2:
            self.color = PURPLE
            self.fire_delay = 1000
            self.aim_spread = 15
            self.move_speed = 2
        else:
            self.color = GRAY
            self.fire_delay = 3000
            self.aim_spread = 40
            self.move_speed = 0.5
    
    def update(self, player_pos, current_time):
        self.move_counter += 16
        
        if self.type == 1:
            if self.move_counter > 2000:
                self.target_y = random.randint(50, HEIGHT - 50)
                self.move_counter = 0
            
            if abs(self.rect.centery - self.target_y) > 5:
                if self.rect.centery < self.target_y:
                    self.rect.y += self.move_speed
                else:
                    self.rect.y -= self.move_speed
        
        elif self.type == 2:
            dy = player_pos[1] - self.rect.centery
            if abs(dy) > 10:
                self.rect.y += self.move_speed if dy > 0 else -self.move_speed
                self.rect.y = max(0, min(HEIGHT - PLAYER_SIZE, self.rect.y))
    
    def can_fire(self, current_time):
        return current_time - self.last_fire > self.fire_delay
    
    def shoot(self, player_pos, current_time):
        if self.can_fire(current_time):
            self.last_fire = current_time
            
            dx = player_pos[0] - self.rect.centerx
            dy = player_pos[1] - self.rect.centery
            
            angle = math.atan2(dy, dx)
            spread_offset = random.uniform(-self.aim_spread, self.aim_spread) * math.pi / 180
            angle += spread_offset
            
            return {
                'x': self.rect.left - 10,
                'y': self.rect.centery,
                'dx': math.cos(angle) * BASE_BULLET_SPEED,
                'dy': math.sin(angle) * BASE_BULLET_SPEED
            }
        return None
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        if self.type == 2:
            pygame.draw.circle(surface, WHITE, self.rect.center, 3)

class Projectile:
    def __init__(self, x, y, dx, dy):
        self.rect = pygame.Rect(x, y, 8, 4)
        self.dx = dx
        self.dy = dy
    
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
    
    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect)

class MenuManager:
    def __init__(self, stats):
        self.stats = stats
        self.current_menu = "main"
        self.skin_scroll = 0
        self.max_skins_shown = 6
        self.buttons = {}
        
    def draw_button(self, surface, text, color, x, y, width, height, hover=False):
        button_rect = pygame.Rect(x, y, width, height)
        if hover:
            pygame.draw.rect(surface, color, button_rect, border_radius=10)
            pygame.draw.rect(surface, WHITE, button_rect, 2, border_radius=10)
            text_color = BLACK if color != BLACK else WHITE
        else:
            pygame.draw.rect(surface, BLACK, button_rect, border_radius=10)
            pygame.draw.rect(surface, color, button_rect, 2, border_radius=10)
            text_color = color
            
        font = pygame.font.SysFont('Arial', 32)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)
        return button_rect
        
    def draw_main_menu(self, surface):
        surface.fill(BLACK)
        
        
        title_font = pygame.font.SysFont('Arial', 64, bold=True)
        subtitle_font = pygame.font.SysFont('Arial', 24)
        info_font = pygame.font.SysFont('Arial', 20)
        
        
        title_text = title_font.render("BOT ESCAPE", True, WHITE)
        glow_text = title_font.render("BOT ESCAPE", True, BLUE)
        subtitle_text = subtitle_font.render("Survival Challenge", True, GRAY)
        
        
        glow_pos = [(WIDTH // 2 - title_text.get_width() // 2 + i, 80) for i in range(-2, 3, 2)]
        for pos in glow_pos:
            surface.blit(glow_text, pos)
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
        surface.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 150))
        
        
        mouse_pos = pygame.mouse.get_pos()
        
        
        button_width = 200
        button_height = 50
        button_x = WIDTH // 2 - button_width // 2
        
        self.buttons = {}
        
        
        play_rect = self.draw_button(surface, "PLAY", GREEN, button_x, 250, 
                                   button_width, button_height, 
                                   pygame.Rect(button_x, 250, button_width, button_height).collidepoint(mouse_pos))
        self.buttons['play'] = play_rect
        
        
        skins_rect = self.draw_button(surface, "SKINS", CYAN, button_x, 320,
                                    button_width, button_height,
                                    pygame.Rect(button_x, 320, button_width, button_height).collidepoint(mouse_pos))
        self.buttons['skins'] = skins_rect
        
        
        quit_rect = self.draw_button(surface, "QUIT", RED, button_x, 390,
                                   button_width, button_height,
                                   pygame.Rect(button_x, 390, button_width, button_height).collidepoint(mouse_pos))
        self.buttons['quit'] = quit_rect
        
        
        level_text = info_font.render(f"Level: {self.stats.player_lvl}", True, WHITE)
        xp_text = info_font.render(f"XP: {self.stats.xp}/{self.stats.xp_target}", True, WHITE)
        best_text = info_font.render(f"Best Time: {self.stats.best_time:.1f}s | Wave: {self.stats.best_wave}", True, YELLOW)
        
        surface.blit(level_text, (20, HEIGHT - 80))
        surface.blit(xp_text, (20, HEIGHT - 60))
        surface.blit(best_text, (20, HEIGHT - 40))
        
        
        xp_bar_w = 200
        xp_bar_h = 8
        xp_fill = self.stats.xp / self.stats.xp_target
        
        
        glow_surf = pygame.Surface((xp_bar_w, xp_bar_h + 4))
        glow_surf.set_alpha(100)
        pygame.draw.rect(glow_surf, GREEN, (0, 0, xp_fill * xp_bar_w, xp_bar_h + 4))
        surface.blit(glow_surf, (18, HEIGHT - 22))
        
        # main XP bar
        pygame.draw.rect(surface, GRAY, (20, HEIGHT - 20, xp_bar_w, xp_bar_h))
        pygame.draw.rect(surface, GREEN, (20, HEIGHT - 20, xp_fill * xp_bar_w, xp_bar_h))
        
        controls_text = info_font.render("Use mouse to navigate menus | WASD to move in game | SPACE to pause", True, GRAY)
        surface.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, HEIGHT - 30))
    
    def draw_skin_menu(self, surface):
        surface.fill(BLACK)
        
        title_font = pygame.font.SysFont('Arial', 36, bold=True)
        menu_font = pygame.font.SysFont('Arial', 24)
        small_font = pygame.font.SysFont('Arial', 18)
        
        title_text = title_font.render("SKIN SELECTION", True, WHITE)
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        
        unlocked_skins = self.get_unlocked_skins()
        start_y = 120
        
        self.skin_buttons = {}
        mouse_pos = pygame.mouse.get_pos()
        
        for i, skin_idx in enumerate(unlocked_skins):
            if i < self.skin_scroll:
                continue
            if i >= self.skin_scroll + self.max_skins_shown:
                break
                
            skin = AVAILABLE_SKINS[skin_idx]
            y_pos = start_y + (i - self.skin_scroll) * 60
            
            is_selected = skin_idx == self.stats.selected_skin
            is_hovered = pygame.Rect(100, y_pos, 600, 50).collidepoint(mouse_pos)
            bg_color = GREEN if is_selected else (WHITE if is_hovered else GRAY)
            text_color = BLACK if (is_selected or is_hovered) else WHITE
            
            skin_rect = pygame.Rect(100, y_pos, 600, 50)
            pygame.draw.rect(surface, bg_color, skin_rect)
            pygame.draw.rect(surface, WHITE, skin_rect, 2)
            self.skin_buttons[skin_idx] = skin_rect
            
            preview_rect = pygame.Rect(120, y_pos + 10, 30, 30)
            if skin.shape == "square":
                pygame.draw.rect(surface, skin.color, preview_rect)
            elif skin.shape == "triangle":
                points = [
                    (preview_rect.centerx, preview_rect.top),
                    (preview_rect.left, preview_rect.bottom),
                    (preview_rect.right, preview_rect.bottom)
                ]
                pygame.draw.polygon(surface, skin.color, points)
            elif skin.shape == "circle":
                pygame.draw.circle(surface, skin.color, preview_rect.center, 15)
            
            name_text = menu_font.render(skin.name, True, text_color)
            level_req_text = small_font.render(f"Unlocked at Level {skin.unlock_level}", True, text_color)
            
            surface.blit(name_text, (170, y_pos + 10))
            surface.blit(level_req_text, (170, y_pos + 30))
        
        locked_count = len(AVAILABLE_SKINS) - len(unlocked_skins)
        if locked_count > 0:
            locked_text = small_font.render(f"{locked_count} skins locked - Level up to unlock more!", True, YELLOW)
            surface.blit(locked_text, (WIDTH // 2 - locked_text.get_width() // 2, start_y + 400))
        
        back_text = menu_font.render("Press ESC to go back, SPACE to select skin", True, WHITE)
        surface.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))
    
    def get_unlocked_skins(self):
        unlocked = []
        for i, skin in enumerate(AVAILABLE_SKINS):
            if skin.unlock_level <= self.stats.player_lvl:
                unlocked.append(i)
        return unlocked
    
    def handle_main_menu_input(self, keys, mouse_pos, mouse_click):
        if keys[pygame.K_SPACE]:
            return "play"
        elif keys[pygame.K_s]:
            self.current_menu = "skins"
        elif keys[pygame.K_ESCAPE]:
            return "quit"
        
        #mouse input
        if mouse_click and self.buttons['play'].collidepoint(mouse_pos):
            return "play"
        elif mouse_click and self.buttons['skins'].collidepoint(mouse_pos):
            self.current_menu = "skins"
        elif mouse_click and self.buttons['quit'].collidepoint(mouse_pos):
            return "quit"
        
        return None
    
    def handle_skin_menu_input(self, keys, mouse_pos, mouse_click):
        unlocked_skins = self.get_unlocked_skins()
        
        if keys[pygame.K_ESCAPE]:
            self.current_menu = "main"
        elif mouse_click or keys[pygame.K_SPACE]:
            if hasattr(self, 'skin_buttons'):
                for skin_idx, button_rect in self.skin_buttons.items():
                    if mouse_click and button_rect.collidepoint(mouse_pos):
                        self.stats.selected_skin = skin_idx
                        save_game_progress(self.stats)
                        break

class GameManager:
    def __init__(self):
        self.stats = GameStats()
        self.menu = MenuManager(self.stats)
        self.game_state = "menu"
        self.is_paused = False
        self.reset_game()
    
    def reset_game(self):
        self.player = Player(100, HEIGHT // 2, self.stats.selected_skin)
        self.enemies = [Enemy(WIDTH - 100, HEIGHT // 2)]
        self.projectiles = []
        self.last_spawn = pygame.time.get_ticks()
        self.game_start = time.time()
        self.is_running = True
        self.is_game_over = False
        self.time_survived = 0
        self.current_wave = 1
        save_game_progress(self.stats)

    def get_wave_settings(self, wave):
        wave_configs = {
            1: {'spawn_interval': 12000, 'max_enemies': 3, 'enemy_types': [0]},
            2: {'spawn_interval': 10000, 'max_enemies': 4, 'enemy_types': [0, 1]},
            3: {'spawn_interval': 8000, 'max_enemies': 5, 'enemy_types': [0, 1]},
            4: {'spawn_interval': 7000, 'max_enemies': 6, 'enemy_types': [0, 1, 2]},
            5: {'spawn_interval': 6000, 'max_enemies': 7, 'enemy_types': [0, 1, 2]},
            6: {'spawn_interval': 5000, 'max_enemies': 8, 'enemy_types': [0, 1, 2, 3]},
            7: {'spawn_interval': 4500, 'max_enemies': 9, 'enemy_types': [0, 1, 2, 3]},
            8: {'spawn_interval': 4000, 'max_enemies': 10, 'enemy_types': [1, 2, 3]},
            9: {'spawn_interval': 3500, 'max_enemies': 12, 'enemy_types': [1, 2, 3]},
            10: {'spawn_interval': 3000, 'max_enemies': 15, 'enemy_types': [2, 3]}
        }
        
        if wave <= 10:
            return wave_configs[wave]
        else:
            return {
                'spawn_interval': max(2000, 3000 - (wave - 10) * 100),
                'max_enemies': min(20, 15 + (wave - 10)),
                'enemy_types': [2, 3]
            }
    
    def calculate_current_wave(self):
        wave_from_time = int(self.time_survived // 15) + 1
        return wave_from_time
    
    def spawn_enemy(self, current_time):
        self.current_wave = self.calculate_current_wave()
        settings = self.get_wave_settings(self.current_wave)
        
        if (current_time - self.last_spawn > settings['spawn_interval'] and 
            len(self.enemies) < settings['max_enemies']):
            
            spawn_y = random.randint(50, HEIGHT - 50)
            enemy_type = random.choice(settings['enemy_types'])
            self.enemies.append(Enemy(WIDTH - 100, spawn_y, enemy_type))
            self.last_spawn = current_time
    
    def update(self):
        if not self.is_running or self.is_paused:
            return
        
        current_time = pygame.time.get_ticks()
        self.time_survived = time.time() - self.game_start
        
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        
        self.spawn_enemy(current_time)
        
        for enemy in self.enemies:
            enemy.update(self.player.rect.center, current_time)
            shot_data = enemy.shoot(self.player.rect.center, current_time)
            if shot_data:
                self.projectiles.append(Projectile(
                    shot_data['x'], shot_data['y'],
                    shot_data['dx'], shot_data['dy']
                ))
        
        for projectile in self.projectiles[:]:
            projectile.update()
            if projectile.rect.colliderect(self.player.rect):
                self.player.hp -= 25
                self.projectiles.remove(projectile)
                if self.player.hp <= 0:
                    self.end_game()
            elif projectile.rect.x < -10 or projectile.rect.x > WIDTH + 10 or projectile.rect.y < -10 or projectile.rect.y > HEIGHT + 10:
                self.projectiles.remove(projectile)
        
        if self.time_survived > 5 and self.player.hp < self.player.max_hp:
            self.player.hp = min(self.player.max_hp, self.player.hp + 0.2)
    
    def end_game(self):
        self.is_running = False
        self.is_game_over = True
        
        if self.time_survived > self.stats.best_time:
            self.stats.best_time = self.time_survived
        
        if self.current_wave > self.stats.best_wave:
            self.stats.best_wave = self.current_wave
        
        earned_xp = int(self.time_survived * 10 + self.current_wave * 20)
        self.stats.xp += earned_xp
        
        level_ups = 0
        while self.stats.xp >= self.stats.xp_target:
            self.stats.xp -= self.stats.xp_target
            self.stats.player_lvl += 1
            self.stats.xp_target = int(self.stats.xp_target * 1.2)
            level_ups += 1
        
        self.level_ups_gained = level_ups
    
    def draw_hud(self, surface):
        font = pygame.font.SysFont('Arial', 24)
        small_font = pygame.font.SysFont('Arial', 18)
        
        time_display = font.render(f"Time: {self.time_survived:.1f}s", True, WHITE)
        wave_display = font.render(f"Wave: {self.current_wave}", True, WHITE)
        best_display = small_font.render(f"Best: {self.stats.best_time:.1f}s", True, WHITE)
        level_display = small_font.render(f"Level: {self.stats.player_lvl}", True, WHITE)
        
        surface.blit(time_display, (10, 10))
        surface.blit(wave_display, (10, 40))
        surface.blit(best_display, (10, 70))
        surface.blit(level_display, (10, 90))
        
        xp_bar_w = 200
        xp_bar_h = 8
        xp_fill = self.stats.xp / self.stats.xp_target
        
        pygame.draw.rect(surface, GRAY, (WIDTH - xp_bar_w - 10, 10, xp_bar_w, xp_bar_h))
        pygame.draw.rect(surface, GREEN, (WIDTH - xp_bar_w - 10, 10, xp_fill * xp_bar_w, xp_bar_h))
        
        xp_display = small_font.render(f"XP: {self.stats.xp}/{self.stats.xp_target}", True, WHITE)
        surface.blit(xp_display, (WIDTH - xp_bar_w - 10, 25))
    
    def draw(self, surface):
        surface.fill(BLACK)
        
        self.player.draw(surface)
        
        for enemy in self.enemies:
            enemy.draw(surface)
        
        for projectile in self.projectiles:
            projectile.draw(surface)
        
        self.draw_hud(surface)
        
        if self.is_paused:
            
            s = pygame.Surface((WIDTH, HEIGHT))
            s.set_alpha(128)
            s.fill(BLACK)
            surface.blit(s, (0,0))
            
            pause_font = pygame.font.SysFont('Arial', 48, bold=True)
            menu_font = pygame.font.SysFont('Arial', 24)
            
            pause_text = pause_font.render("PAUSED", True, WHITE)
            resume_text = menu_font.render("Click here or press SPACE to resume", True, WHITE)
            menu_button = menu_font.render("Back to Menu", True, WHITE)
            
            
            pause_x = WIDTH // 2 - pause_text.get_width() // 2
            pause_y = HEIGHT // 2 - pause_text.get_height() - 40
            surface.blit(pause_text, (pause_x, pause_y))
            
            
            resume_x = WIDTH // 2 - resume_text.get_width() // 2
            resume_y = HEIGHT // 2 
            surface.blit(resume_text, (resume_x, resume_y))
            
            
            menu_x = WIDTH // 2 - menu_button.get_width() // 2
            menu_y = HEIGHT // 2 + 50
            menu_rect = pygame.Rect(menu_x - 10, menu_y - 5, menu_button.get_width() + 20, menu_button.get_height() + 10)
            pygame.draw.rect(surface, GRAY, menu_rect, border_radius=5)
            surface.blit(menu_button, (menu_x, menu_y))
    
    def show_death_screen(self, surface):
        surface.fill(BLACK)
        
        title_font = pygame.font.SysFont('Arial', 36)
        normal_font = pygame.font.SysFont('Arial', 24)
        small_font = pygame.font.SysFont('Arial', 18)
        
        game_over_text = title_font.render("GAME OVER", True, RED)
        time_text = normal_font.render(f"Survival Time: {self.time_survived:.2f}s", True, WHITE)
        wave_text = normal_font.render(f"Max Wave Reached: {self.current_wave}", True, WHITE)
        
        earned_xp = int(self.time_survived * 10 + self.current_wave * 20)
        xp_text = small_font.render(f"XP Earned: +{earned_xp}", True, YELLOW)
        
        if hasattr(self, 'level_ups_gained') and self.level_ups_gained > 0:
            level_up_text = small_font.render(f"LEVEL UP! +{self.level_ups_gained} levels!", True, GREEN)
        else:
            level_up_text = None
        
        record_time = small_font.render(f"Personal Best: {self.stats.best_time:.2f}s", True, GREEN)
        record_wave = small_font.render(f"Best Wave: {self.stats.best_wave}", True, GREEN)
        
        restart_text = normal_font.render("Press E to play again, M for menu, ESC to quit", True, WHITE)
        
        y_offset = HEIGHT // 2 - 120
        surface.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, y_offset))
        surface.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, y_offset + 50))
        surface.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, y_offset + 80))
        surface.blit(xp_text, (WIDTH // 2 - xp_text.get_width() // 2, y_offset + 110))
        
        if level_up_text:
            surface.blit(level_up_text, (WIDTH // 2 - level_up_text.get_width() // 2, y_offset + 130))
            y_offset += 20
        
        surface.blit(record_time, (WIDTH // 2 - record_time.get_width() // 2, y_offset + 150))
        surface.blit(record_wave, (WIDTH // 2 - record_wave.get_width() // 2, y_offset + 170))
        surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, y_offset + 200))

def main():
    game = GameManager()
    mouse_click = False
    mouse_pos = (0, 0)
    
    while True:
        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game_progress(game.stats)
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  
                    mouse_click = True
                    mouse_pos = event.pos
                    
                    if game.game_state == "menu":
                        if game.menu.current_menu == "main":
                            for button, rect in game.menu.buttons.items():
                                if rect.collidepoint(mouse_pos):
                                    if button == "play":
                                        game.game_state = "playing"
                                        game.reset_game()
                                    elif button == "skins":
                                        game.menu.current_menu = "skins"
                                    elif button == "quit":
                                        pygame.quit()
                                        sys.exit()
                                        
                    elif game.game_state == "playing" and game.is_paused:
                        
                        menu_font = pygame.font.SysFont('Arial', 24)
                        menu_button = menu_font.render("Back to Menu", True, WHITE)
                        menu_x = WIDTH // 2 - menu_button.get_width() // 2
                        menu_y = HEIGHT // 2 + 50
                        menu_rect = pygame.Rect(menu_x - 10, menu_y - 5, 
                                             menu_button.get_width() + 20, 
                                             menu_button.get_height() + 10)
                        
                        if menu_rect.collidepoint(mouse_pos):
                            game.game_state = "menu"
                            game.menu.current_menu = "main"
                            game.is_paused = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.game_state == "playing" and not game.is_game_over:
                        game.is_paused = not game.is_paused
                elif event.key == pygame.K_ESCAPE:
                    if game.game_state == "playing":
                        game.is_paused = True
        
        keys = pygame.key.get_pressed()
        
        if game.game_state == "menu":
            if game.menu.current_menu == "main":
                game.menu.draw_main_menu(screen)
            elif game.menu.current_menu == "skins":
                game.menu.draw_skin_menu(screen)
                game.menu.handle_skin_menu_input(keys, mouse_pos, mouse_click)
        
        elif game.game_state == "playing":
            if game.is_running:
                game.update()
                game.draw(screen)
            elif game.is_game_over:
                game.show_death_screen(screen)
                
                if keys[pygame.K_e]:
                    game.reset_game()
                elif keys[pygame.K_m] or keys[pygame.K_ESCAPE]:
                    save_game_progress(game.stats)
                    game.game_state = "menu"
                    game.menu.current_menu = "main"
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
