import pygame
import sys
import math
import random
from cpu_ai import CPUAI, CPUDifficulty, ActionType
from character_specific_ai import CharacterSpecificAI, CharacterStyle

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
STAGE_HEIGHT = 100
PLATFORM_HEIGHT = 20
PLATFORM_WIDTH = 200
GRAVITY = 0.5
JUMP_STRENGTH = 10
MOVE_SPEED = 5
MAX_DAMAGE = 300
DEATH_BOUNDARY_BOTTOM = SCREEN_HEIGHT + 100
DEATH_BOUNDARY_SIDES = 100
STARTING_LIVES = 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BROWN = (165, 42, 42)
GRAY = (128, 128, 128)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Smash Bros AI Demo")
clock = pygame.time.Clock()

class Character:
    def __init__(self, x, y, color, name="Generic", is_cpu=False, difficulty=CPUDifficulty.MEDIUM, playstyle=None):
        self.spawn_x = x
        self.spawn_y = y
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.color = color
        self.name = name
        self.is_cpu = is_cpu
        self.x_velocity = 0
        self.y_velocity = 0
        self.is_jumping = False
        self.damage = 0
        self.is_shielding = False
        self.shield_time = 0
        self.is_attacking = False
        self.attack_time = 0
        self.attack_type = None
        self.is_dodging = False
        self.dodge_time = 0
        self.dodge_direction = (0, 0)
        self.is_using_special = False
        self.special_move = None
        self.special_time = 0
        self.hitstun = 0
        self.facing_right = True
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.lives = STARTING_LIVES
        self.respawn_timer = 0
        self.is_dead = False
        self.invulnerable = 0
        
        if is_cpu:
            if playstyle:
                self.ai = CharacterSpecificAI(name, difficulty, playstyle)
            else:
                self.ai = CPUAI(difficulty)
        else:
            self.ai = None
    
    def update(self, platforms, opponent):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer == 0:
                self.respawn()
            return
            
        if self.invulnerable > 0:
            self.invulnerable -= 1
        
        self.y_velocity += GRAVITY
        
        self.x += self.x_velocity
        self.y += self.y_velocity
        
        self.is_jumping = True
        for platform in platforms:
            if self.y_velocity > 0:
                if platform.top <= self.y + self.height <= platform.top + 10:
                    if platform.left <= self.x + self.width//2 <= platform.right:
                        self.y = platform.top - self.height
                        self.y_velocity = 0
                        self.is_jumping = False
        
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            
        self.rect.x = self.x
        self.rect.y = self.y
        
        self.is_off_stage = self.y > SCREEN_HEIGHT - STAGE_HEIGHT
        
        if self.check_death():
            return
            
        if self.is_shielding:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.is_shielding = False
                
        if self.is_attacking:
            self.attack_time -= 1
            if self.attack_time <= 0:
                self.is_attacking = False
                self.attack_type = None
                
        if self.is_dodging:
            self.dodge_time -= 1
            if self.dodge_time <= 0:
                self.is_dodging = False
                
        if self.is_using_special:
            self.special_time -= 1
            if self.special_time <= 0:
                self.is_using_special = False
                self.special_move = None
                
        if self.hitstun > 0:
            self.hitstun -= 1
            
        if self.x_velocity > 0:
            self.facing_right = True
        elif self.x_velocity < 0:
            self.facing_right = False
        
        if self.is_cpu and self.hitstun <= 0 and not (self.is_attacking or self.is_dodging or self.is_shielding or self.is_using_special):
            self.update_ai(opponent)
    
    def check_death(self):
        """Check if character should be considered dead and lose a life."""
        if self.y > DEATH_BOUNDARY_BOTTOM:
            self.die()
            return True
            
        if self.x < -DEATH_BOUNDARY_SIDES or self.x > SCREEN_WIDTH + DEATH_BOUNDARY_SIDES:
            self.die()
            return True
            
        if self.damage >= MAX_DAMAGE and (abs(self.x_velocity) > 15 or abs(self.y_velocity) > 15):
            self.die()
            return True
            
        return False
    
    def die(self):
        """Handle character death."""
        self.lives -= 1
        self.is_dead = True
        if self.lives > 0:
            self.respawn_timer = 90  
        else:
            pass
    
    def respawn(self):
        """Respawn the character."""
        self.is_dead = False
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.x_velocity = 0
        self.y_velocity = 0
        self.damage = 0
        self.is_jumping = False
        self.is_shielding = False
        self.is_attacking = False
        self.is_dodging = False
        self.is_using_special = False
        self.hitstun = 0
        self.invulnerable = 120 
    
    def update_ai(self, opponent):
        """Update AI and perform actions based on AI decisions."""
        game_state = {
            'position': (self.x, self.y),
            'enemy_position': (opponent.x, opponent.y),
            'enemy_distance': math.sqrt((self.x - opponent.x)**2 + (self.y - opponent.y)**2),
            'damage': self.damage,
            'off_stage': self.is_off_stage,
            'in_air': self.is_jumping,
            'enemy_attacking_nearby': opponent.is_attacking and math.sqrt((self.x - opponent.x)**2 + (self.y - opponent.y)**2) < 60,
            'enemy_in_range': math.sqrt((self.x - opponent.x)**2 + (self.y - opponent.y)**2) < 80,
            'stage_center': (SCREEN_WIDTH//2, SCREEN_HEIGHT - STAGE_HEIGHT - 10),
            'stage_direction': (0 if abs(self.x - SCREEN_WIDTH//2) < 10 else 
                               -1 if self.x > SCREEN_WIDTH//2 else 1, 
                               1 if self.y > SCREEN_HEIGHT - STAGE_HEIGHT else 0),
        }
        
        action = self.ai.update(game_state)
        
        if action["type"] == ActionType.IDLE:
            self.x_velocity = 0
            
        elif action["type"] == ActionType.MOVE:
            direction = action.get('direction', (0, 0))
            self.x_velocity = direction[0] * MOVE_SPEED
            if direction[1] < -0.5 and not self.is_jumping:
                self.y_velocity = -JUMP_STRENGTH
                
        elif action["type"] == ActionType.ATTACK:
            self.perform_attack(action.get('attack_type', 'jab'))
            
        elif action["type"] == ActionType.SHIELD:
            self.perform_shield(action.get('duration', 30))
            
        elif action["type"] == ActionType.DODGE:
            direction = action.get('direction', (random.uniform(-1, 1), 0))
            self.perform_dodge(direction)
            
        elif action["type"] == ActionType.RECOVER:
            direction = action.get('direction', (0, -1))
            self.y_velocity = -JUMP_STRENGTH * 1.5
            self.x_velocity = direction[0] * MOVE_SPEED
            
        elif action["type"] == ActionType.SPECIAL:
            self.perform_special(action.get('special_move', 'special_neutral'))
    
    def perform_attack(self, attack_type):
        self.is_attacking = True
        self.attack_type = attack_type
        self.attack_time = 20
        self.x_velocity = 0
    
    def perform_shield(self, duration):
        self.is_shielding = True
        self.shield_time = duration * FPS // 2
        self.x_velocity = 0
    
    def perform_dodge(self, direction):
        self.is_dodging = True
        self.dodge_time = 15
        self.dodge_direction = direction
        self.x_velocity = direction[0] * MOVE_SPEED * 2
    
    def perform_special(self, special_move):
        self.is_using_special = True
        self.special_move = special_move
        self.special_time = 30
        self.x_velocity = 0
    
    def draw(self, screen):
        if self.respawn_timer > 0:
            font = pygame.font.SysFont(None, 36)
            resp_text = font.render(f"{self.name} respawning in {self.respawn_timer//20 + 1}", True, self.color)
            screen.blit(resp_text, (SCREEN_WIDTH//2 - resp_text.get_width()//2, 100))
            return
            
        if self.is_dead and self.lives <= 0:
            return
        
        character_color = self.color
        if self.invulnerable > 0 and self.invulnerable % 10 < 5:
            character_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(character_surface, (*self.color, 128), (0, 0, self.width, self.height))
            screen.blit(character_surface, (self.x, self.y))
        else:
            pygame.draw.rect(screen, character_color, (self.x, self.y, self.width, self.height))
        
        eye_x = self.x + (self.width * 0.75 if self.facing_right else self.width * 0.25)
        pygame.draw.circle(screen, BLACK, (int(eye_x), int(self.y + self.height * 0.25)), 5)
        
        if self.is_shielding:
            shield_radius = self.width * 0.8
            shield_surface = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 200, 255, 128), (shield_radius, shield_radius), shield_radius)
            screen.blit(shield_surface, (int(self.x + self.width//2 - shield_radius), 
                                        int(self.y + self.height//2 - shield_radius)))
        
        if self.is_attacking:
            attack_width = self.width * 0.8
            attack_height = self.height * 0.4
            
            if "jab" in self.attack_type:
                punch_x = self.x + self.width if self.facing_right else self.x - attack_width
                pygame.draw.rect(screen, YELLOW, 
                                (punch_x, self.y + self.height * 0.4, 
                                 attack_width, attack_height))
                
            elif "smash" in self.attack_type:
                smash_x = self.x + self.width * 1.2 if self.facing_right else self.x - attack_width * 1.2
                pygame.draw.rect(screen, RED, 
                                (smash_x, self.y + self.height * 0.3, 
                                 attack_width * 1.2, attack_height * 1.2))
                
            elif "aerial" in self.attack_type:
                if "up" in self.attack_type:
                    pygame.draw.rect(screen, GREEN, 
                                    (self.x, self.y - attack_height, 
                                     self.width, attack_height))
                elif "down" in self.attack_type:
                    pygame.draw.rect(screen, GREEN, 
                                    (self.x, self.y + self.height, 
                                     self.width, attack_height))
                else:
                    aerial_x = self.x + self.width if self.facing_right else self.x - attack_width
                    pygame.draw.rect(screen, GREEN, 
                                    (aerial_x, self.y + self.height * 0.3, 
                                     attack_width, attack_height))
        
        if self.is_using_special:
            if "neutral" in self.special_move:
                special_x = self.x + self.width * 1.5 if self.facing_right else self.x - self.width * 0.8
                special_width = self.width * 0.5
                pygame.draw.circle(screen, BLUE, 
                                  (int(special_x), int(self.y + self.height * 0.5)), 
                                  int(special_width))
                
            elif "up" in self.special_move:
                pygame.draw.rect(screen, BLUE, 
                                (self.x, self.y - self.height * 0.8, 
                                 self.width, self.height * 0.8))
                
            elif "down" in self.special_move:
                pygame.draw.rect(screen, BLUE, 
                                (self.x - self.width * 0.3, self.y + self.height, 
                                 self.width * 1.6, self.height * 0.5))
                
            elif "forward" in self.special_move:
                special_x = self.x + self.width if self.facing_right else self.x - self.width
                pygame.draw.rect(screen, BLUE, 
                                (special_x, self.y, 
                                 self.width, self.height))
        
        font = pygame.font.SysFont(None, 24)
        damage_text = font.render(f"{int(self.damage)}%", True, BLACK)
        screen.blit(damage_text, (self.x, self.y - 25))
        
        name_text = font.render(f"{self.name} × {self.lives}", True, BLACK)
        screen.blit(name_text, (self.x, self.y - 45))

def draw_blast_zones(screen):
    """Draw visual indicators for the blast zones (death boundaries)."""
    pygame.draw.line(screen, RED, (0, DEATH_BOUNDARY_BOTTOM), 
                    (SCREEN_WIDTH, DEATH_BOUNDARY_BOTTOM), 2)
    
    pygame.draw.line(screen, RED, (-DEATH_BOUNDARY_SIDES, 0), 
                    (-DEATH_BOUNDARY_SIDES, SCREEN_HEIGHT), 2)
    pygame.draw.line(screen, RED, (SCREEN_WIDTH + DEATH_BOUNDARY_SIDES, 0), 
                    (SCREEN_WIDTH + DEATH_BOUNDARY_SIDES, SCREEN_HEIGHT), 2)

def reset_game(player, cpu):
    """Reset the game state for both characters."""
    player.lives = STARTING_LIVES
    player.damage = 0
    player.is_dead = False
    player.respawn()
    
    cpu.lives = STARTING_LIVES
    cpu.damage = 0
    cpu.is_dead = False
    cpu.respawn()

def main():
    main_stage = pygame.Rect(SCREEN_WIDTH//2 - PLATFORM_WIDTH, SCREEN_HEIGHT - STAGE_HEIGHT, 
                            PLATFORM_WIDTH * 2, PLATFORM_HEIGHT)
    left_platform = pygame.Rect(SCREEN_WIDTH//4 - PLATFORM_WIDTH//2, SCREEN_HEIGHT - STAGE_HEIGHT * 2, 
                               PLATFORM_WIDTH//2, PLATFORM_HEIGHT)
    right_platform = pygame.Rect(SCREEN_WIDTH * 3//4 - PLATFORM_WIDTH//2, SCREEN_HEIGHT - STAGE_HEIGHT * 2, 
                                PLATFORM_WIDTH//2, PLATFORM_HEIGHT)
    platforms = [main_stage, left_platform, right_platform]
    
    player = Character(SCREEN_WIDTH//4, SCREEN_HEIGHT - STAGE_HEIGHT - 100, RED, "Player", is_cpu=False)
    cpu = Character(SCREEN_WIDTH * 3//4, SCREEN_HEIGHT - STAGE_HEIGHT - 100, BLUE, "Mario", 
                   is_cpu=True, difficulty=CPUDifficulty.MEDIUM, 
                   playstyle=CharacterStyle.AGGRESSIVE)
    
    action_text = ""
    font = pygame.font.SysFont(None, 28)
    game_over = False
    winner = None
    
    running = True
    frame_count = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game(player, cpu)
                game_over = False
                winner = None
            
            if not game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.x_velocity = -MOVE_SPEED
                if event.key == pygame.K_RIGHT:
                    player.x_velocity = MOVE_SPEED
                if event.key == pygame.K_UP and not player.is_jumping:
                    player.y_velocity = -JUMP_STRENGTH
                if event.key == pygame.K_z:
                    player.perform_attack("jab")
                if event.key == pygame.K_x:
                    player.perform_special("special_neutral")
                if event.key == pygame.K_c:
                    player.perform_shield(30)
                if event.key == pygame.K_v:
                    player.perform_dodge((player.x_velocity, 0))
                    
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    player.x_velocity = 0
        
        if not game_over:
            player.update(platforms, cpu)
            cpu.update(platforms, player)
            
            if player.lives <= 0 or cpu.lives <= 0:
                game_over = True
                winner = "CPU" if player.lives <= 0 else "Player"
            
            if player.is_attacking and not cpu.is_dodging and not cpu.is_shielding and cpu.invulnerable <= 0:
                attack_rect = pygame.Rect(
                    player.x + player.width if player.facing_right else player.x - player.width * 0.8,
                    player.y, 
                    player.width * 0.8, 
                    player.height
                )
                if attack_rect.colliderect(cpu.rect):
                    knockback = 5 + cpu.damage / 10
                    direction = 1 if player.facing_right else -1
                    cpu.x_velocity = knockback * direction
                    cpu.y_velocity = -knockback / 2
                    cpu.damage += random.randint(5, 10)
                    cpu.hitstun = 10
            
            if cpu.is_attacking and not player.is_dodging and not player.is_shielding and player.invulnerable <= 0:
                attack_rect = pygame.Rect(
                    cpu.x + cpu.width if cpu.facing_right else cpu.x - cpu.width * 0.8,
                    cpu.y, 
                    cpu.width * 0.8, 
                    cpu.height
                )
                if attack_rect.colliderect(player.rect):
                    knockback = 5 + player.damage / 10
                    direction = 1 if cpu.facing_right else -1
                    player.x_velocity = knockback * direction
                    player.y_velocity = -knockback / 2
                    player.damage += random.randint(5, 10)
                    player.hitstun = 10
            
            if frame_count % 30 == 0 and cpu.ai:
                state = {
                    'position': (cpu.x, cpu.y),
                    'enemy_position': (player.x, player.y),
                    'enemy_distance': math.sqrt((cpu.x - player.x)**2 + (cpu.y - player.y)**2),
                    'damage': cpu.damage,
                    'off_stage': cpu.is_off_stage,
                    'in_air': cpu.is_jumping,
                    'enemy_attacking_nearby': player.is_attacking,
                    'enemy_in_range': math.sqrt((cpu.x - player.x)**2 + (cpu.y - player.y)**2) < 80,
                }
                
                if cpu.is_attacking:
                    action_text = f"CPU: Attacking ({cpu.attack_type})"
                elif cpu.is_shielding:
                    action_text = f"CPU: Shielding"
                elif cpu.is_dodging:
                    action_text = f"CPU: Dodging"
                elif cpu.is_using_special:
                    action_text = f"CPU: Special ({cpu.special_move})"
                elif cpu.hitstun > 0:
                    action_text = f"CPU: In hitstun"
                elif cpu.respawn_timer > 0:
                    action_text = f"CPU: Respawning"
                else:
                    action_text = f"CPU: Moving/Positioning"
        
        screen.fill(WHITE)
        
        draw_blast_zones(screen)
        
        for platform in platforms:
            pygame.draw.rect(screen, BROWN, platform)
        
        player.draw(screen)
        cpu.draw(screen)
        
        text_surface = font.render(action_text, True, BLACK)
        screen.blit(text_surface, (20, 20))
        
        if not game_over:
            controls_text = font.render("Controls: Arrows=Move, Z=Attack, X=Special, C=Shield, V=Dodge", True, BLACK)
            screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 30))
        
        if game_over:
            game_over_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            game_over_surf.fill((0, 0, 0, 128))
            screen.blit(game_over_surf, (0, 0))
            
            big_font = pygame.font.SysFont(None, 72)
            med_font = pygame.font.SysFont(None, 48)
            
            game_over_text = big_font.render("GAME OVER", True, WHITE)
            winner_text = med_font.render(f"{winner} WINS!", True, WHITE)
            restart_text = med_font.render("Press R to restart", True, WHITE)
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 80))
            screen.blit(winner_text, (SCREEN_WIDTH//2 - winner_text.get_width()//2, SCREEN_HEIGHT//2))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 80))
        
        pygame.display.flip()
        clock.tick(FPS)
        frame_count += 1
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()