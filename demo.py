from cpu_ai import CPUAI, CPUDifficulty, ActionType
import time
import random

def create_sample_game_state(player_pos, cpu_pos, cpu_damage):
    """Create a sample game state for demonstration."""
    enemy_distance = ((player_pos[0] - cpu_pos[0])**2 + (player_pos[1] - cpu_pos[1])**2)**0.5
    
    return {
        'position': cpu_pos,
        'enemy_position': player_pos,
        'enemy_distance': enemy_distance,
        'damage': cpu_damage,
        'off_stage': cpu_pos[1] < -50 or abs(cpu_pos[0]) > 200,
        'in_air': cpu_pos[1] > 0,
        'enemy_attacking_nearby': enemy_distance < 30 and random.random() < 0.3,
        'enemy_in_range': enemy_distance < 50,
        'stage_center': (0, 0),
        'stage_direction': (0 if abs(cpu_pos[0]) < 10 else -1 if cpu_pos[0] > 0 else 1, 
                           1 if cpu_pos[1] < 0 else 0),
    }

def simulate_movement(pos, direction, speed=5):
    """Simulate movement in a direction."""
    return (pos[0] + direction[0] * speed, pos[1] + direction[1] * speed)

def print_action(action):
    """Print a human-readable description of the AI action."""
    if action["type"] == ActionType.IDLE:
        print(f"CPU is idling for {action.get('duration', 0):.2f} seconds")
    elif action["type"] == ActionType.MOVE:
        direction = action.get('direction', (0, 0))
        print(f"CPU is moving in direction: ({direction[0]:.2f}, {direction[1]:.2f})")
    elif action["type"] == ActionType.ATTACK:
        print(f"CPU is using attack: {action.get('attack_type', 'unknown')}")
    elif action["type"] == ActionType.SHIELD:
        print(f"CPU is shielding for {action.get('duration', 0):.2f} seconds")
    elif action["type"] == ActionType.DODGE:
        direction = action.get('direction', (0, 0))
        print(f"CPU is dodging in direction: ({direction[0]:.2f}, {direction[1]:.2f})")
    elif action["type"] == ActionType.RECOVER:
        direction = action.get('direction', (0, 0))
        print(f"CPU is recovering in direction: ({direction[0]:.2f}, {direction[1]:.2f})")
    elif action["type"] == ActionType.SPECIAL:
        print(f"CPU is using special move: {action.get('special_move', 'unknown')}")

def main():
    cpu_ai = CPUAI(difficulty=CPUDifficulty.MEDIUM)
    
    player_pos = (100, 0)
    cpu_pos = (-50, 0)
    cpu_damage = 0
    
    print("Starting CPU AI simulation")
    print("--------------------------")
    
    for i in range(20):
        print(f"\nFrame {i+1}")
        print(f"Player position: ({player_pos[0]:.1f}, {player_pos[1]:.1f})")
        print(f"CPU position: ({cpu_pos[0]:.1f}, {cpu_pos[1]:.1f})")
        print(f"CPU damage: {cpu_damage}%")
        
        game_state = create_sample_game_state(player_pos, cpu_pos, cpu_damage)
        
        action = cpu_ai.update(game_state)
        print_action(action)
        
        if action["type"] == ActionType.MOVE or action["type"] == ActionType.RECOVER:
            cpu_pos = simulate_movement(cpu_pos, action.get('direction', (0, 0)))
        
        if random.random() < 0.7:
            direction = (random.uniform(-1, 1), random.uniform(-1, 1))
            player_pos = simulate_movement(player_pos, direction, speed=3)
        
        if random.random() < 0.2:
            cpu_damage += random.randint(5, 15)
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()