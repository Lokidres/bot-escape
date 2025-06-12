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

PLAYER_SIZE = 35
BASE_SPEED = 4
BASE_BULLET_SPEED = 6

class GameStats:
    def __init__(self):
        self.best_time = 0
        self.best_wave = 1
        self.player_lvl = 1
        self.xp = 0
        self.xp_target = 100

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = BASE_SPEED
        self.hp = 100
        self.max_hp = 100
        
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
        pygame.draw.rect(surface, BLUE, self.rect)
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

class GameManager:
    def __init__(self):
        self.stats = GameStats()
        self.reset_game()
    
    def reset_game(self):
        self.player = Player(100, HEIGHT // 2)
        self.enemies = [Enemy(WIDTH - 100, HEIGHT // 2)]
        self.projectiles = []
        self.last_spawn = pygame.time.get_ticks()
        self.game_start = time.time()
        self.is_running = True
        self.is_game_over = False
        self.time_survived = 0
        self.current_wave = 1
    
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
        if not self.is_running:
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
        
        while self.stats.xp >= self.stats.xp_target:
            self.stats.xp -= self.stats.xp_target
            self.stats.player_lvl += 1
            self.stats.xp_target = int(self.stats.xp_target * 1.2)
    
    def draw_hud(self, surface):
        font = pygame.font.SysFont('Arial', 24)
        small_font = pygame.font.SysFont('Arial', 18)
        
        time_display = font.render(f"Time: {self.time_survived:.1f}s", True, WHITE)
        wave_display = font.render(f"Wave: {self.current_wave}", True, WHITE)
        best_display = small_font.render(f"Best: {self.stats.best_time:.1f}s", True, WHITE)
        
        surface.blit(time_display, (10, 10))
        surface.blit(wave_display, (10, 40))
        surface.blit(best_display, (10, 70))
    
    def draw(self, surface):
        surface.fill(BLACK)
        
        self.player.draw(surface)
        
        for enemy in self.enemies:
            enemy.draw(surface)
        
        for projectile in self.projectiles:
            projectile.draw(surface)
        
        self.draw_hud(surface)
    
    def show_death_screen(self, surface):
        surface.fill(BLACK)
        
        title_font = pygame.font.SysFont('Arial', 36)
        normal_font = pygame.font.SysFont('Arial', 24)
        small_font = pygame.font.SysFont('Arial', 18)
        
        game_over_text = title_font.render("GAME OVER", True, RED)
        time_text = normal_font.render(f"Survival Time: {self.time_survived:.2f}s", True, WHITE)
        wave_text = normal_font.render(f"Max Wave Reached: {self.current_wave}", True, WHITE)
        record_time = small_font.render(f"Personal Best: {self.stats.best_time:.2f}s", True, GREEN)
        record_wave = small_font.render(f"Best Wave: {self.stats.best_wave}", True, GREEN)
        
        restart_text = normal_font.render("Press E to play again, ESC to quit", True, WHITE)
        
        surface.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
        surface.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 - 50))
        surface.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, HEIGHT // 2 - 20))
        surface.blit(record_time, (WIDTH // 2 - record_time.get_width() // 2, HEIGHT // 2 + 20))
        surface.blit(record_wave, (WIDTH // 2 - record_wave.get_width() // 2, HEIGHT // 2 + 45))
        surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 80))

def main():
    game = GameManager()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        if game.is_running:
            game.update()
            game.draw(screen)
        
        elif game.is_game_over:
            game.show_death_screen(screen)
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e]:
                game.reset_game()
            elif keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
