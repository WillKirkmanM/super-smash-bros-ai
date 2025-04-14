import random
from enum import Enum

class ActionType(Enum):
    IDLE = 0
    MOVE = 1
    ATTACK = 2
    SHIELD = 3
    DODGE = 4
    RECOVER = 5
    SPECIAL = 6

class CPUDifficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2
    INTENSE = 3

class CPUAI:
    def __init__(self, difficulty=CPUDifficulty.MEDIUM):
        self.difficulty = difficulty
        self.reaction_time = self._set_reaction_time()
        self.decision_weights = self._set_decision_weights()
        self.last_action = None
        self.current_state = None
        
    def _set_reaction_time(self):
        """Set reaction time based on difficulty."""
        if self.difficulty == CPUDifficulty.EASY:
            return random.uniform(0.3, 0.5)
        elif self.difficulty == CPUDifficulty.MEDIUM:
            return random.uniform(0.2, 0.3)
        elif self.difficulty == CPUDifficulty.HARD:
            return random.uniform(0.1, 0.2)
        else:
            return random.uniform(0.05, 0.1)
    
    def _set_decision_weights(self):
        """Set decision making preferences based on difficulty."""
        if self.difficulty == CPUDifficulty.EASY:
            return {
                ActionType.IDLE: 0.2,
                ActionType.MOVE: 0.4,
                ActionType.ATTACK: 0.3,
                ActionType.SHIELD: 0.05,
                ActionType.DODGE: 0.05,
                ActionType.RECOVER: 0.7,
                ActionType.SPECIAL: 0.1
            }
        elif self.difficulty == CPUDifficulty.MEDIUM:
            return {
                ActionType.IDLE: 0.1,
                ActionType.MOVE: 0.3,
                ActionType.ATTACK: 0.3,
                ActionType.SHIELD: 0.1,
                ActionType.DODGE: 0.1,
                ActionType.RECOVER: 0.8,
                ActionType.SPECIAL: 0.2
            }
        elif self.difficulty == CPUDifficulty.HARD:
            return {
                ActionType.IDLE: 0.05,
                ActionType.MOVE: 0.25,
                ActionType.ATTACK: 0.3,
                ActionType.SHIELD: 0.2,
                ActionType.DODGE: 0.15,
                ActionType.RECOVER: 0.9,
                ActionType.SPECIAL: 0.25
            }
        else:
            return {
                ActionType.IDLE: 0.02,
                ActionType.MOVE: 0.2,
                ActionType.ATTACK: 0.35,
                ActionType.SHIELD: 0.25,
                ActionType.DODGE: 0.25,
                ActionType.RECOVER: 0.95,
                ActionType.SPECIAL: 0.3
            }
    
    def update(self, game_state):
        """
        Update AI state and decide on an action.
        
        Args:
            game_state: Current state of the game including character positions,
                        damage percentages, stage hazards, etc.
        
        Returns:
            action: The decided action to take
        """
        self.current_state = game_state
        
        if self._is_in_danger():
            return self._defensive_action()
        
        if self._is_enemy_approachable():
            return {"type": ActionType.MOVE, "direction": self._best_approach_direction()}
        
        if self._can_attack():
            return self._offensive_action()
        
        return self._neutral_action()
    
    def _is_in_danger(self):
        """Determine if CPU is in a dangerous situation."""
        
        if not self.current_state:
            return False
            
        if self._is_off_stage():
            return True
            
        if self.current_state.get('damage', 0) > 80:
            if random.random() < 0.3 * (self.current_state.get('damage', 0) / 100):
                return True
                
        if self._enemy_attacking_nearby():
            return True
            
        return False
    
    def _can_attack(self):
        """Determine if CPU can attack an opponent."""
        if not self.current_state:
            return False
            
        enemy_distance = self.current_state.get('enemy_distance', float('inf'))
        
        return enemy_distance < 60
    
    def _is_enemy_approachable(self):
        """Determine if we should approach the enemy."""
        enemy_distance = self.current_state.get('enemy_distance', float('inf'))
        return enemy_distance >= 60
    
    def _defensive_action(self):
        """Choose a defensive action based on the situation."""
        if self._is_off_stage():
            if random.random() < self.decision_weights[ActionType.RECOVER]:
                return {"type": ActionType.RECOVER, "direction": self._best_recovery_direction()}
        
        choices = [
            (ActionType.SHIELD, self.decision_weights[ActionType.SHIELD]),
            (ActionType.DODGE, self.decision_weights[ActionType.DODGE]),
            (ActionType.MOVE, self.decision_weights[ActionType.MOVE] * 0.5)
        ]
        
        action_type = self._weighted_choice(choices)
        
        if action_type == ActionType.SHIELD:
            return {"type": ActionType.SHIELD, "duration": random.uniform(0.2, 1.0)}
        elif action_type == ActionType.DODGE:
            return {"type": ActionType.DODGE, "direction": self._best_dodge_direction()}
        else:
            return {"type": ActionType.MOVE, "direction": self._direction_away_from_danger()}
    
    def _offensive_action(self):
        """Choose an offensive action based on the situation."""
        choices = [
            (ActionType.ATTACK, self.decision_weights[ActionType.ATTACK] * 1.5),
            (ActionType.SPECIAL, self.decision_weights[ActionType.SPECIAL]),
        ]
        
        action_type = self._weighted_choice(choices)
        
        if action_type == ActionType.ATTACK:
            return {"type": ActionType.ATTACK, "attack_type": self._choose_attack()}
        else:
            return {"type": ActionType.SPECIAL, "special_move": self._choose_special()}
    
    def _neutral_action(self):
        """Choose an action when not directly attacking or defending."""
        choices = [
            (ActionType.MOVE, self.decision_weights[ActionType.MOVE]),
            (ActionType.IDLE, self.decision_weights[ActionType.IDLE]),
            (ActionType.ATTACK, self.decision_weights[ActionType.ATTACK] * 0.2)
        ]
        
        action_type = self._weighted_choice(choices)
        
        if action_type == ActionType.MOVE:
            return {"type": ActionType.MOVE, "direction": self._strategic_movement()}
        elif action_type == ActionType.ATTACK:
            return {"type": ActionType.ATTACK, "attack_type": self._choose_attack()}
        else:
            return {"type": ActionType.IDLE, "duration": random.uniform(0.1, 0.5)}
    
    
    def _weighted_choice(self, choices):
        """Make a weighted random choice from a list of options."""
        total = sum(weight for _, weight in choices)
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in choices:
            if upto + weight >= r:
                return choice
            upto += weight
        return choices[-1][0]
    
    def _is_off_stage(self):
        """Check if the character is off the stage and needs to recover."""
        return self.current_state.get('off_stage', False)
    
    def _enemy_attacking_nearby(self):
        """Check if an enemy is nearby and attacking."""
        return self.current_state.get('enemy_attacking_nearby', False)
    
    def _enemy_in_range(self):
        """Check if an enemy is within attack range."""
        return self.current_state.get('enemy_in_range', False)
    
    def _best_recovery_direction(self):
        """Calculate the best direction for recovery."""
        return self.current_state.get('stage_direction', (0, 1))
    
    def _best_dodge_direction(self):
        """Calculate the best direction to dodge."""
        return self._direction_away_from_danger()
    
    def _direction_away_from_danger(self):
        """Calculate direction away from danger."""
        enemy_pos = self.current_state.get('enemy_position', (0, 0))
        self_pos = self.current_state.get('position', (0, 0))
        
        dx = self_pos[0] - enemy_pos[0]
        dy = self_pos[1] - enemy_pos[1]
        
        magnitude = (dx**2 + dy**2)**0.5
        if magnitude == 0:
            return (random.uniform(-1, 1), random.uniform(-1, 1))
        return (dx/magnitude, dy/magnitude)
    
    def _best_approach_direction(self):
        """Calculate the best direction to approach an enemy."""
        enemy_pos = self.current_state.get('enemy_position', (0, 0))
        self_pos = self.current_state.get('position', (0, 0))
        
        dx = enemy_pos[0] - self_pos[0]
        dy = enemy_pos[1] - self_pos[1]
        
        magnitude = (dx**2 + dy**2)**0.5
        if magnitude == 0:
            return (random.uniform(-1, 1), random.uniform(-1, 1))
        return (dx/magnitude, dy/magnitude)
    
    def _strategic_movement(self):
        """Calculate a strategic movement direction."""
        
        if random.random() < 0.7:
            return self._best_approach_direction()
        else:
            self_pos = self.current_state.get('position', (0, 0))
            center = self.current_state.get('stage_center', (0, 0))
            
            dx = center[0] - self_pos[0]
            dy = center[1] - self_pos[1]
            
            magnitude = (dx**2 + dy**2)**0.5
            if magnitude == 0:
                return (random.uniform(-1, 1), random.uniform(-1, 1))
            return (dx/magnitude, dy/magnitude)
    
    def _choose_attack(self):
        """Choose an attack type based on the situation."""
        options = ["jab", "tilt_up", "tilt_down", "tilt_forward", 
                  "smash_up", "smash_down", "smash_forward", 
                  "aerial_up", "aerial_down", "aerial_forward", "aerial_backward", "aerial_neutral"]
        
        
        if self.current_state.get('in_air', False):
            return random.choice(["aerial_up", "aerial_down", "aerial_forward", 
                                 "aerial_backward", "aerial_neutral"])
        else:
            enemy_distance = self.current_state.get('enemy_distance', 100)
            if enemy_distance < 20:
                return random.choice(["jab", "tilt_up", "tilt_down", "tilt_forward"])
            else:
                return random.choice(["smash_up", "smash_down", "smash_forward"])
    
    def _choose_special(self):
        """Choose a special move based on the situation."""
        options = ["special_neutral", "special_up", "special_down", "special_forward"]
        
        
        if self._is_off_stage():
            return "special_up"
        else:
            return random.choice(options)