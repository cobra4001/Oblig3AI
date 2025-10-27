import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
DARK_BLUE = (70, 130, 180)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 215, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
CLOUD_WHITE = (250, 250, 250)
GRASS_GREEN = (124, 252, 0)
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)
GOLD = (255, 215, 0)
BLUE = (0, 100, 255)

# Particle system
class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, lifetime=30):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.uniform(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.vx *= 0.95
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 0:
            try:
                surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(surface, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
                screen.blit(surface, (int(self.x - self.size), int(self.y - self.size)))
            except:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class GlowEffect:
    def __init__(self, x, y, radius, color, intensity=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.lifetime = intensity
    
    def update(self):
        self.lifetime -= 0.5
        return self.lifetime > 0
    
    def draw(self, screen):
        if self.lifetime > 0:
            alpha_ratio = self.lifetime / self.intensity
            current_radius = int(self.radius * alpha_ratio)
            if current_radius > 0:
                for i in range(5):
                    r = current_radius + i * 5
                    alpha = int(30 * alpha_ratio)
                    if r > 0 and alpha > 0:
                        try:
                            surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                            pygame.draw.circle(surface, (*self.color, alpha), (r, r), r)
                            screen.blit(surface, (self.x - r, self.y - r))
                        except:
                            pass

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type  # 'shield', 'magnet', 'double'
        self.rect = pygame.Rect(x, y, 30, 30)
        self.animation = 0
        
        if power_type == 'shield':
            self.color = CYAN
        elif power_type == 'magnet':
            self.color = PURPLE
        elif power_type == 'double':
            self.color = GOLD
        else:
            self.color = WHITE
    
    def update(self):
        self.animation += 0.2
    
    def draw(self, screen):
        size = 15 + int(math.sin(self.animation) * 3)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), size, 2)
        
        # Icon based on type
        if self.type == 'shield':
            # Shield icon
            pass
        elif self.type == 'slow':
            # Clock icon
            pass
        elif self.type == 'magnet':
            # Magnet icon
            pass
        elif self.type == 'double':
            # 2x icon
            pass

class Cloud:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(0.7, 1.3)
        self.speed = random.uniform(0.5, 1.5)
        self.z = random.uniform(0.5, 2.0)
        self.puffs = []
        self.generate_puffs()
    
    def generate_puffs(self):
        for i in range(8):
            self.puffs.append({
                'x': random.uniform(-40, 40) * self.size,
                'y': random.uniform(-20, 20) * self.size,
                'size': random.uniform(15, 40) * self.size * self.z,
                'opacity': random.uniform(0.6, 0.95)
            })
    
    def update(self):
        self.x -= self.speed * self.z
        if self.x < -300:
            self.x = SCREEN_WIDTH + 150
            self.y = random.randint(50, 250)
            self.z = random.uniform(0.5, 2.0)
    
    def draw(self, screen):
        for puff in sorted(self.puffs, key=lambda p: p['y']):
            x = int(self.x + puff['x'])
            y = int(self.y + puff['y'])
            size = int(puff['size'])
            opacity = puff['opacity']
            
            try:
                surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                color = (*CLOUD_WHITE, int(255 * opacity))
                pygame.draw.circle(surface, color, (size, size), size)
                screen.blit(surface, (x - size, y - size))
            except:
                pass

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.gravity = 0.6
        self.jump_strength = -11
        self.width = 45
        self.height = 32
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.angle = 0
        self.wing_flap = 0
        self.trail = []
        self.last_positions = []
        
        # Power-ups
        self.shield_active = False
        self.shield_timer = 0
        self.slow_motion_active = False
        self.slow_motion_timer = 0
        self.magnet_active = False
        self.magnet_timer = 0
        self.double_points_active = False
        self.double_points_timer = 0
    
    def jump(self):
        self.velocity = self.jump_strength
        self.wing_flap = 10
    
    def update(self):
        # Update power-up timers
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
        
        if self.slow_motion_active:
            self.slow_motion_timer -= 1
            if self.slow_motion_timer <= 0:
                self.slow_motion_active = False
        
        if self.magnet_active:
            self.magnet_timer -= 1
            if self.magnet_timer <= 0:
                self.magnet_active = False
        
        if self.double_points_active:
            self.double_points_timer -= 1
            if self.double_points_timer <= 0:
                self.double_points_active = False
        
        # Apply slow motion effect
        gravity = self.gravity * (0.5 if self.slow_motion_active else 1.0)
        self.velocity += gravity
        self.y += self.velocity
        
        # Magnet effect - easier control
        if self.magnet_active:
            self.velocity *= 1.1  # Slight upward pull
        
        self.last_positions.append((int(self.x + self.width // 2), int(self.y + self.height // 2)))
        if len(self.last_positions) > 15:
            self.last_positions.pop(0)
        
        self.angle = -self.velocity * 3
        self.angle = max(-45, min(45, self.angle))
        
        self.rect.y = self.y
        self.wing_flap = max(0, self.wing_flap - 0.5)
    
    def draw(self, screen):
        # Shield effect
        if self.shield_active:
            shield_radius = self.width + 20
            shield_color = CYAN if int(self.shield_timer / 5) % 2 == 0 else (0, 255, 255)
            pygame.draw.circle(screen, shield_color, 
                             (int(self.x + self.width // 2), int(self.y + self.height // 2)), 
                             shield_radius, 3)
        
        # Motion blur trail
        if len(self.last_positions) > 2:
            for i, pos in enumerate(self.last_positions[:-1]):
                alpha = i * 15
                if alpha < 200 and i > 0:
                    try:
                        size = int(8 * (i / len(self.last_positions)))
                        surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                        pygame.draw.circle(surface, (255, 215, 0, alpha // 2), (size, size), size)
                        screen.blit(surface, (pos[0] - size, pos[1] - size))
                    except:
                        pass
        
        # Wing animation
        flap_offset = math.sin(self.wing_flap) * 5
        wing_points = [
            (self.x + 20, self.y + 15),
            (self.x + 35, self.y + 10 + flap_offset),
            (self.x + 25, self.y + 25),
        ]
        
        pygame.draw.polygon(screen, (220, 200, 0), wing_points)
        pygame.draw.ellipse(screen, YELLOW, self.rect)
        
        # Head
        head_rect = pygame.Rect(self.x + 10, self.y + 3, 22, 20)
        pygame.draw.ellipse(screen, YELLOW, head_rect)
        
        # Eye
        eye_x = int(self.x + 18)
        eye_y = int(self.y + 10)
        pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 8)
        pygame.draw.circle(screen, BLACK, (eye_x + 2, eye_y), 4)
        pygame.draw.circle(screen, WHITE, (eye_x + 3, eye_y - 1), 2)
        
        # Beak
        beak_points = [(self.x + 35, self.y + 13), (self.x + 48, self.y + 15), (self.x + 35, self.y + 19)]
        pygame.draw.polygon(screen, ORANGE, beak_points)

class Pipe:
    def __init__(self, x, gap_height):
        self.x = x
        self.width = 80
        self.gap = 200
        self.top_height = random.randint(100, gap_height)
        self.bottom_y = self.top_height + self.gap
        self.speed = 3
        self.cap_height = 20
        
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        # Top pipe with shading
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        pygame.draw.rect(screen, GREEN, top_rect)
        
        for i in range(10):
            shade_color = tuple(max(0, c - i * 8) for c in GREEN)
            pygame.draw.rect(screen, shade_color, (self.x + i, 0, 8, self.top_height))
        
        pygame.draw.rect(screen, (100, 180, 100), (self.x, 0, 15, self.top_height))
        
        # Top cap
        cap_top = pygame.Rect(self.x - 5, self.top_height - self.cap_height, self.width + 10, self.cap_height)
        pygame.draw.rect(screen, DARK_GREEN, cap_top)
        
        # Bottom pipe
        bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y)
        pygame.draw.rect(screen, GREEN, bottom_rect)
        
        for i in range(10):
            shade_color = tuple(max(0, c - i * 8) for c in GREEN)
            pygame.draw.rect(screen, shade_color, (self.x + i, self.bottom_y, 8, SCREEN_HEIGHT - self.bottom_y))
        
        pygame.draw.rect(screen, (100, 180, 100), (self.x, self.bottom_y, 15, SCREEN_HEIGHT - self.bottom_y))
        
        # Bottom cap
        cap_bottom = pygame.Rect(self.x - 5, self.bottom_y, self.width + 10, self.cap_height)
        pygame.draw.rect(screen, DARK_GREEN, cap_bottom)
    
    def get_collision_rects(self):
        return [
            pygame.Rect(self.x, 0, self.width, self.top_height),
            pygame.Rect(self.x, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y),
            pygame.Rect(self.x - 5, self.top_height - self.cap_height, self.width + 10, self.cap_height),
            pygame.Rect(self.x - 5, self.bottom_y, self.width + 10, self.cap_height)
        ]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird - Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.high_score_file = "highscore.txt"
        self.high_score = self.load_high_score()
        self.new_record = False
        self.reset()
    
    def load_high_score(self):
        """Load high score from file"""
        try:
            with open(self.high_score_file, 'r') as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0
    
    def save_high_score(self, score):
        """Save high score to file"""
        try:
            with open(self.high_score_file, 'w') as f:
                f.write(str(score))
        except:
            pass
    
    def reset(self):
        self.bird = Bird(100, SCREEN_HEIGHT // 2)
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.scored_pipes = set()
        self.new_record = False
        
        for i in range(3):
            self.pipes.append(Pipe(SCREEN_WIDTH + i * 400, SCREEN_HEIGHT - 150))
        
        self.clouds = []
        for i in range(5):
            self.clouds.append(Cloud(random.randint(0, SCREEN_WIDTH * 2), random.randint(50, 250)))
        
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.ground_height = 50
        
        self.particles = []
        self.glow_effects = []
        
        self.screen_shake_x = 0
        self.screen_shake_y = 0
        self.screen_shake_intensity = 0
        
        # Power-ups
        self.power_ups = []
        self.power_up_spawn_timer = 0
    
    def add_screen_shake(self, intensity=10):
        self.screen_shake_intensity += intensity
        self.screen_shake_intensity = min(self.screen_shake_intensity, 30)
    
    def create_star_particles(self, x, y):
        for _ in range(15):
            self.particles.append(Particle(x, y, YELLOW, random.uniform(-3, 3), random.uniform(-6, -2), random.randint(20, 40)))
        self.glow_effects.append(GlowEffect(x, y, 50, YELLOW, 15))
        self.add_screen_shake(3)
    
    def create_collision_particles(self, x, y):
        for _ in range(30):
            self.particles.append(Particle(x, y, RED, random.uniform(-8, 8), random.uniform(-8, 8), random.randint(15, 30)))
        self.add_screen_shake(20)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if self.game_over:
                        self.reset()
                    else:
                        self.bird.jump()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.reset()
                else:
                    self.bird.jump()
        return True
    
    def update(self):
        if self.game_over:
            self.particles = [p for p in self.particles if p.update()]
            self.glow_effects = [g for g in self.glow_effects if g.update()]
            self.screen_shake_intensity *= 0.9
            self.screen_shake_x = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
            self.screen_shake_y = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
            return
        
        if self.screen_shake_intensity > 0.1:
            self.screen_shake_intensity *= 0.9
            self.screen_shake_x = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
            self.screen_shake_y = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
        else:
            self.screen_shake_x = 0
            self.screen_shake_y = 0
        
        self.particles = [p for p in self.particles if p.update()]
        self.glow_effects = [g for g in self.glow_effects if g.update()]
        
        # Spawn power-ups occasionally
        self.power_up_spawn_timer += 1
        if self.power_up_spawn_timer > 180 and random.random() < 0.01 and not self.game_over:
            # Find a safe location away from pipes
            pu_x = SCREEN_WIDTH + 50
            safe_y = None
            attempts = 0
            
            # Try to find a safe Y position
            while safe_y is None and attempts < 50:
                test_y = random.randint(150, SCREEN_HEIGHT - 250)
                is_safe = True
                
                # Check if this position is too close to any pipe
                for pipe in self.pipes:
                    pipe_distance = abs(pipe.x - pu_x)
                    if pipe_distance < 200:  # Only check nearby pipes
                        # Check if the test_y is in the solid pipe area (NOT safe)
                        if test_y < pipe.top_height or test_y > pipe.bottom_y:
                            is_safe = False
                            break
                
                if is_safe:
                    safe_y = test_y
                
                attempts += 1
            
            if safe_y is not None:
                power_types = ['shield', 'magnet', 'double']
                self.power_ups.append(PowerUp(pu_x, safe_y, random.choice(power_types)))
                self.power_up_spawn_timer = 0
        
        # Update power-ups
        for pu in self.power_ups:
            pu.x -= 3  # Move with pipes
            pu.rect.x = pu.x
            pu.rect.y = pu.y
            pu.update()
            
            # Check collision
            if self.bird.rect.colliderect(pu.rect) and not self.game_over:
                if pu.type == 'shield':
                    self.bird.shield_active = True
                    self.bird.shield_timer = 600  # 10 seconds at 60 FPS
                elif pu.type == 'magnet':
                    self.bird.magnet_active = True
                    self.bird.magnet_timer = 1200  # 20 seconds
                elif pu.type == 'double':
                    self.bird.double_points_active = True
                    self.bird.double_points_timer = 1800  # 30 seconds
                
                self.create_star_particles(pu.x, pu.y)
                self.power_ups.remove(pu)
        
        self.power_ups = [pu for pu in self.power_ups if pu.x > -50]
        
        self.bird.update()
        
        ground_y = SCREEN_HEIGHT - self.ground_height
        if self.bird.y < 0 or self.bird.y + self.bird.height > ground_y:
            self.game_over = True
            # Check for new high score
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score(self.score)
                self.new_record = True
            self.create_collision_particles(int(self.bird.x + self.bird.width // 2), int(self.bird.y + self.bird.height // 2))
        
        for cloud in self.clouds:
            cloud.update()
        
        old_score = self.score
        for pipe in self.pipes:
            pipe.update()
            
            for rect in pipe.get_collision_rects():
                if self.bird.rect.colliderect(rect) and not self.bird.shield_active:
                    self.game_over = True
                    # Check for new high score
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score(self.score)
                        self.new_record = True
                    self.create_collision_particles(int(self.bird.x + self.bird.width // 2), int(self.bird.y + self.bird.height // 2))
                    break
            
            if pipe.x + pipe.width < self.bird.x and pipe not in self.scored_pipes:
                points = 2 if self.bird.double_points_active else 1
                self.score += points
                self.scored_pipes.add(pipe)
                gap_center_y = pipe.top_height + (pipe.bottom_y - pipe.top_height) // 2
                self.create_star_particles(pipe.x + pipe.width // 2, gap_center_y)
        
        self.pipes = [pipe for pipe in self.pipes if pipe.x + pipe.width > 0]
        
        if self.pipes and self.pipes[-1].x < SCREEN_WIDTH - 400:
            self.pipes.append(Pipe(SCREEN_WIDTH, SCREEN_HEIGHT - 150))
            self.pipes = [pipe for pipe in self.pipes if pipe.x > -200]
    
    def draw(self):
        # Sky gradient
        for y in range(SCREEN_HEIGHT - self.ground_height):
            color_value = min(255, 135 + y // 3)
            color = (color_value, 206, min(255, 235 + y // 4))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Clouds
        sorted_clouds = sorted(self.clouds, key=lambda c: c.z, reverse=True)
        for cloud in sorted_clouds:
            cloud.draw(self.screen)
        
        if not self.game_over:
            ground_y = SCREEN_HEIGHT - self.ground_height
            pygame.draw.rect(self.screen, GRASS_GREEN, (0, ground_y, SCREEN_WIDTH, self.ground_height))
            
            for x in range(0, SCREEN_WIDTH, 20):
                for i in range(3):
                    grass_start_x = x + i * 6
                    pygame.draw.line(self.screen, (100, 200, 100), 
                                   (grass_start_x, ground_y), 
                                   (grass_start_x + random.randint(-5, 5), ground_y - random.randint(5, 15)), 2)
            
            pygame.draw.line(self.screen, DARK_GREEN, (0, ground_y), (SCREEN_WIDTH, ground_y), 3)
            
            for pipe in self.pipes:
                pipe.draw(self.screen)
            
            # Draw power-ups
            for pu in self.power_ups:
                pu.draw(self.screen)
            
            for glow in self.glow_effects:
                glow.draw(self.screen)
            
            for particle in self.particles:
                particle.draw(self.screen)
            
            self.bird.draw(self.screen)
            
            score_shadow = self.font.render(str(self.score), True, BLACK)
            score_text = self.font.render(str(self.score), True, YELLOW)
            self.screen.blit(score_shadow, (SCREEN_WIDTH // 2 - 18 + self.screen_shake_x, 52 + self.screen_shake_y))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 20 + self.screen_shake_x, 50 + self.screen_shake_y))
            
            # High score in top right
            high_score_display = self.small_font.render(f"Best: {self.high_score}", True, WHITE)
            self.screen.blit(high_score_display, (SCREEN_WIDTH - 120, 10))
            
            # Power-up indicators
            y_offset = 10
            if self.bird.shield_active:
                status = self.small_font.render(f"SHIELD {int(self.bird.shield_timer/60)}s", True, CYAN)
                self.screen.blit(status, (10, y_offset))
                y_offset += 30
            if self.bird.magnet_active:
                status = self.small_font.render(f"MAGNET {int(self.bird.magnet_timer/60)}s", True, PURPLE)
                self.screen.blit(status, (10, y_offset))
                y_offset += 30
            if self.bird.double_points_active:
                status = self.small_font.render(f"2X POINTS {int(self.bird.double_points_timer/60)}s", True, GOLD)
                self.screen.blit(status, (10, y_offset))
                y_offset += 30
        
        else:
            ground_y = SCREEN_HEIGHT - self.ground_height
            pygame.draw.rect(self.screen, GRASS_GREEN, (0, ground_y, SCREEN_WIDTH, self.ground_height))
            pygame.draw.line(self.screen, DARK_GREEN, (0, ground_y), (SCREEN_WIDTH, ground_y), 3)
            
            for glow in self.glow_effects:
                glow.draw(self.screen)
            for particle in self.particles:
                particle.draw(self.screen)
            
            shake_x = self.screen_shake_x
            shake_y = self.screen_shake_y
            
            game_over_shadow = self.font.render("Game Over", True, BLACK)
            game_over_text = self.font.render("Game Over", True, RED)
            score_text_shadow = self.font.render(f"Score: {self.score}", True, BLACK)
            score_text = self.font.render(f"Score: {self.score}", True, YELLOW)
            restart_shadow = self.small_font.render("Press SPACE to restart", True, BLACK)
            restart_text = self.small_font.render("Press SPACE to restart", True, WHITE)
            
            self.screen.blit(game_over_shadow, (SCREEN_WIDTH // 2 - 148 + shake_x, SCREEN_HEIGHT // 2 - 98 + shake_y))
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150 + shake_x, SCREEN_HEIGHT // 2 - 100 + shake_y))
            
            self.screen.blit(score_text_shadow, (SCREEN_WIDTH // 2 - 78 + shake_x, SCREEN_HEIGHT // 2 + 2 + shake_y))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 80 + shake_x, SCREEN_HEIGHT // 2 + shake_y))
            
            # High score display
            high_score_text = self.small_font.render(f"Best: {self.high_score}", True, YELLOW)
            high_score_shadow = self.small_font.render(f"Best: {self.high_score}", True, BLACK)
            self.screen.blit(high_score_shadow, (SCREEN_WIDTH // 2 - 68 + shake_x, SCREEN_HEIGHT // 2 + 52 + shake_y))
            self.screen.blit(high_score_text, (SCREEN_WIDTH // 2 - 70 + shake_x, SCREEN_HEIGHT // 2 + 50 + shake_y))
            
            # New record notification
            if self.new_record:
                record_text = self.font.render("NEW RECORD!", True, GOLD)
                self.screen.blit(record_text, (SCREEN_WIDTH // 2 - 100 + shake_x, SCREEN_HEIGHT // 2 + 90 + shake_y))
            
            self.screen.blit(restart_shadow, (SCREEN_WIDTH // 2 - 148 + shake_x, SCREEN_HEIGHT // 2 + 130 + shake_y))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150 + shake_x, SCREEN_HEIGHT // 2 + 128 + shake_y))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

