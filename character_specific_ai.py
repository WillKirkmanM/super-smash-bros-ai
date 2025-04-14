from cpu_ai import CPUAI, CPUDifficulty, ActionType
import random

class CharacterStyle:
    """Define playstyle characteristics for different character archetypes."""
    
    BALANCED = {
        ActionType.IDLE: 1.0,
        ActionType.MOVE: 1.0,
        ActionType.ATTACK: 1.0,
        ActionType.SHIELD: 1.0,
        ActionType.DODGE: 1.0,
        ActionType.RECOVER: 1.0,
        ActionType.SPECIAL: 1.0
    }
    
    AGGRESSIVE = {
        ActionType.IDLE: 0.5,
        ActionType.MOVE: 1.2,
        ActionType.ATTACK: 1.5,
        ActionType.SHIELD: 0.7,
        ActionType.DODGE: 0.8,
        ActionType.RECOVER: 1.0,
        ActionType.SPECIAL: 1.3
    }
    
    DEFENSIVE = {
        ActionType.IDLE: 0.8,
        ActionType.MOVE: 0.9,
        ActionType.ATTACK: 0.8,
        ActionType.SHIELD: 1.5,
        ActionType.DODGE: 1.4,
        ActionType.RECOVER: 1.2,
        ActionType.SPECIAL: 0.9
    }
    
    TECHNICAL = {
        ActionType.IDLE: 0.6,
        ActionType.MOVE: 1.1,
        ActionType.ATTACK: 1.0,
        ActionType.SHIELD: 1.1,
        ActionType.DODGE: 1.2,
        ActionType.RECOVER: 1.0,
        ActionType.SPECIAL: 1.4
    }
    
    BAIT_AND_PUNISH = {
        ActionType.IDLE: 1.2,
        ActionType.MOVE: 1.1,
        ActionType.ATTACK: 0.9,
        ActionType.SHIELD: 1.3,
        ActionType.DODGE: 1.3,
        ActionType.RECOVER: 1.0,
        ActionType.SPECIAL: 0.8
    }
    
    AERIAL = {
        ActionType.IDLE: 0.7,
        ActionType.MOVE: 1.2,
        ActionType.ATTACK: 1.2,
        ActionType.SHIELD: 0.8,
        ActionType.DODGE: 1.0,
        ActionType.RECOVER: 1.1,
        ActionType.SPECIAL: 1.1
    }

class CharacterSpecificAI(CPUAI):
    """AI that adapts behavior based on character specifics."""
    
    def __init__(self, character_name, difficulty=CPUDifficulty.MEDIUM, playstyle=CharacterStyle.BALANCED):
        super().__init__(difficulty)
        self.character_name = character_name
        self.playstyle = playstyle
        self.character_specific_moves = self._set_character_moves()
        
        self._apply_playstyle_modifiers()
        
    def _apply_playstyle_modifiers(self):
        """Apply playstyle modifiers to base decision weights."""
        for action_type, modifier in self.playstyle.items():
            if action_type in self.decision_weights:
                self.decision_weights[action_type] *= modifier
    
    def _set_character_moves(self):
        """Set character-specific move properties and preferences."""
        character_data = {
            "mario": {
                "special_neutral": {"name": "Fireball", "range": "long", "priority": 0.7},
                "special_up": {"name": "Super Jump Punch", "range": "short", "priority": 0.8},
                "special_down": {"name": "F.L.U.D.D.", "range": "medium", "priority": 0.5},
                "special_forward": {"name": "Cape", "range": "short", "priority": 0.6},
                "preferred_attacks": ["aerial_up", "smash_up", "aerial_forward"]
            },
            "link": {
                "special_neutral": {"name": "Bow and Arrow", "range": "long", "priority": 0.9},
                "special_up": {"name": "Spin Attack", "range": "medium", "priority": 0.8},
                "special_down": {"name": "Remote Bomb", "range": "medium", "priority": 0.7},
                "special_forward": {"name": "Boomerang", "range": "long", "priority": 0.8},
                "preferred_attacks": ["smash_forward", "aerial_down", "tilt_up"]
            },
        }
        
        return character_data.get(self.character_name.lower(), {
            "special_neutral": {"name": "Neutral Special", "range": "medium", "priority": 0.5},
            "special_up": {"name": "Up Special", "range": "short", "priority": 0.5},
            "special_down": {"name": "Down Special", "range": "medium", "priority": 0.5},
            "special_forward": {"name": "Forward Special", "range": "medium", "priority": 0.5},
            "preferred_attacks": []
        })
    
    def _choose_special(self):
        """Override to use character-specific special move preferences."""
        if self._is_off_stage():
            return "special_up"
        
        specials = [
            ("special_neutral", self.character_specific_moves.get("special_neutral", {}).get("priority", 0.5)),
            ("special_up", self.character_specific_moves.get("special_up", {}).get("priority", 0.5)),
            ("special_down", self.character_specific_moves.get("special_down", {}).get("priority", 0.5)),
            ("special_forward", self.character_specific_moves.get("special_forward", {}).get("priority", 0.5))
        ]
        
        enemy_distance = self.current_state.get('enemy_distance', 100)
        for i, (move, priority) in enumerate(specials):
            move_range = self.character_specific_moves.get(move, {}).get("range", "medium")
            
            if move_range == "long" and enemy_distance > 70:
                specials[i] = (move, priority * 1.5)
            elif move_range == "medium" and 30 < enemy_distance < 70:
                specials[i] = (move, priority * 1.3)
            elif move_range == "short" and enemy_distance < 30:
                specials[i] = (move, priority * 1.5)
        
        return self._weighted_choice(specials)
    
    def _choose_attack(self):
        """Override to use character-specific attack preferences."""
        preferred = self.character_specific_moves.get("preferred_attacks", [])
        
        options = ["jab", "tilt_up", "tilt_down", "tilt_forward", 
                  "smash_up", "smash_down", "smash_forward", 
                  "aerial_up", "aerial_down", "aerial_forward", "aerial_backward", "aerial_neutral"]
        
        if self.current_state.get('in_air', False):
            filtered_options = [opt for opt in options if "aerial" in opt]
        else:
            filtered_options = [opt for opt in options if "aerial" not in opt]
            
        weighted_options = []
        for opt in filtered_options:
            if opt in preferred:
                weighted_options.append((opt, 2.0))
            else:
                weighted_options.append((opt, 1.0))
        
        enemy_distance = self.current_state.get('enemy_distance', 100)
        for i, (attack, weight) in enumerate(weighted_options):
            if "smash" in attack and 20 < enemy_distance < 40:
                weighted_options[i] = (attack, weight * 1.3)
            elif "tilt" in attack and enemy_distance < 30:
                weighted_options[i] = (attack, weight * 1.2)
            elif "jab" in attack and enemy_distance < 15:
                weighted_options[i] = (attack, weight * 1.5)
                
        return self._weighted_choice(weighted_options)