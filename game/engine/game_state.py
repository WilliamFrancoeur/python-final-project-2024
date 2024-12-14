from typing import Dict, List, Tuple, Optional
import random
from math import sqrt
from ..entities.entity import Entity
from .level_generator import LevelGenerator
from config import GAME_CONFIG


class GameState:
    """
    Manages the core game state including entities, combat, movement, and level management.

    The GameState class is organized into several logical sections:
    1. Initialization and Setup
    2. Entity Management
    3. Movement and Collision
    4. Combat and Health
    5. Level Management
    6. State Serialization
    """

    # -----------------
    # Initialization and Setup
    # -----------------

    def __init__(self):
        """Initialize the game state with default values."""
        self.width = GAME_CONFIG['MAP_WIDTH']
        self.height = GAME_CONFIG['MAP_HEIGHT']
        self.entities: Dict[int, Entity] = {}
        self.next_entity_id = 1
        self.current_level = 1
        self.messages: List[str] = []
        self.walls: List[Tuple[int, int]] = []
        self.game_over = False
        self.combat_this_turn = False
        self.initialize_level()

    def initialize_level(self) -> None:
        """Initialize or reset the current level."""
        self.game_over = False
        self.combat_this_turn = False
        self.entities.clear()
        self.messages.clear()

        # Generate the level
        level = LevelGenerator.create_level(self.current_level)
        if not LevelGenerator.validate_level(level):
            self.messages.append(f"Warning: Level {self.current_level} may have issues!")

        # Set level properties
        self.width = level.width
        self.height = level.height
        self.walls = level.walls.copy()

        # Add player
        self.add_entity(Entity(
            x=level.player_start[0],
            y=level.player_start[1],
            entity_type='player',
            health=GAME_CONFIG['INITIAL_PLAYER_HEALTH'],
            attack=GAME_CONFIG['PLAYER_BASE_DAMAGE']
        ))

        # Add enemies
        for enemy_data in level.get_enemy_spawn_data(self.current_level):
            self.add_entity(Entity(
                x=enemy_data['x'],
                y=enemy_data['y'],
                entity_type='enemy',
                health=enemy_data['health'],
                attack=enemy_data['attack'],
                behavior=enemy_data['behavior']
            ))

    def increment_level(self):
        self.current_level += 1
    # -----------------
    # Entity Management
    # -----------------

    def add_entity(self, entity: Entity) -> int:
        """Add an entity to the game state and return its ID."""
        entity_id = self.next_entity_id
        self.entities[entity_id] = entity
        self.next_entity_id += 1
        return entity_id

    def get_player(self) -> Tuple[int, Entity]:
        """Get the player entity and its ID."""
        for entity_id, entity in self.entities.items():
            if entity.entity_type == 'player':
                return entity_id, entity
        raise ValueError("Player not found in game state")

    # -----------------
    # Movement and Collision
    # -----------------

    def is_valid_move(self, x: int, y: int) -> bool:
        """Check if a position is valid to move to."""
        # Check basic bounds and walls
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        if (x, y) in self.walls:
            return False

        # Check for living entities at the position
        for entity in self.entities.values():
            if entity.x == x and entity.y == y:
                # Allow moving onto squares with dead enemies
                if entity.entity_type == 'enemy' and entity.behavior == 'dead':
                    continue
                return False

        return True

    def get_movement_direction(self, from_x: int, from_y: int, to_x: int, to_y: int) -> Tuple[int, int]:
        """Calculate the best single-step movement direction towards a target."""
        dx = to_x - from_x
        dy = to_y - from_y

        # Normalize to single-step movements (-1, 0, or 1 in each direction)
        move_x = max(min(dx, 1), -1)
        move_y = max(min(dy, 1), -1)

        return (move_x, move_y)

    # -----------------
    # Combat and Health
    # -----------------

    def process_enemy_turns(self):
        """Process all enemy movements and attacks."""
        player_id, player = self.get_player()

        # Process each enemy's turn
        for entity_id, entity in list(self.entities.items()):
            if entity.entity_type != 'enemy' or entity.behavior == 'dead':
                continue

            # Calculate distance to player
            dx = player.x - entity.x
            dy = player.y - entity.y
            distance = sqrt(dx * dx + dy * dy)

            # Check if enemy is in attack range (adjacent, including diagonals)
            if distance <= sqrt(2):  # sqrt(2) allows diagonal attacks
                # Enemy attempts to attack
                if random.random() >= GAME_CONFIG['PLAYER_EVASION_CHANCE']:
                    # Attack hits
                    player.health -= entity.attack
                    self.combat_this_turn = True  # Set combat flag for hit
                    self.messages.append(f"Enemy attacks for {entity.attack} damage!")
                else:
                    self.combat_this_turn = True  # Set combat flag even for miss
                    self.messages.append("You dodge an enemy's attack!")
            else:
                # Enemy moves towards player
                move_x, move_y = self.get_movement_direction(entity.x, entity.y, player.x, player.y)
                new_x = entity.x + move_x
                new_y = entity.y + move_y

                # If direct path is blocked, try alternate moves
                if not self.is_valid_move(new_x, new_y):
                    if move_x != 0 and self.is_valid_move(entity.x + move_x, entity.y):
                        new_x = entity.x + move_x
                        new_y = entity.y
                    elif move_y != 0 and self.is_valid_move(entity.x, entity.y + move_y):
                        new_x = entity.x
                        new_y = entity.y + move_y
                    else:
                        continue  # No valid move found

                # Update enemy position
                entity.x = new_x
                entity.y = new_y

        # Check for player death after all enemy actions
        if player.health <= 0:
            player.health = 0
            player.behavior = 'dead'
            self.game_over = True
            self.messages.append("You have been defeated! Click Reset to try again.")


    def try_move_player(self, target_x: int, target_y: int) -> bool:
        """Handle player movement or attack action."""
        if self.game_over:
            return False

        self.combat_this_turn = False

        try:
            player_id, player = self.get_player()
            dx, dy = self.get_movement_direction(player.x, player.y, target_x, target_y)
            new_x = player.x + dx
            new_y = player.y + dy

            if dx == 0 and dy == 0:
                return False

            # Check for enemies at the target position
            enemy_at_target = None
            for eid, entity in self.entities.items():
                if (entity.entity_type == 'enemy' and
                        entity.x == new_x and
                        entity.y == new_y and
                        entity.health > 0):
                    enemy_at_target = entity
                    break

            action_taken = False

            # Handle combat if enemy present
            if enemy_at_target:
                enemy_at_target.health -= player.attack
                self.combat_this_turn = True  # Set combat flag for player attack
                self.messages.append(f"You attack the enemy for {player.attack} damage!")
                action_taken = True

                if enemy_at_target.health <= 0:
                    self.messages.append("Enemy defeated!")
                    enemy_at_target.behavior = 'dead'
                    player.health += GAME_CONFIG['PLAYER_HEALTH_REGEN_AFTER_KILL']
                    self.messages.append("You regained 8 health! ")

            # Handle movement if no enemy
            elif self.is_valid_move(new_x, new_y):
                # Move the player
                old_x, old_y = player.x, player.y
                player.x = new_x
                player.y = new_y
                action_taken = True

                # Add movement message
                directions = []
                if new_y < old_y:
                    directions.append("north")
                elif new_y > old_y:
                    directions.append("south")
                if new_x > old_x:
                    directions.append("east")
                elif new_x < old_x:
                    directions.append("west")
                direction_str = "-".join(directions) if directions else "nowhere"

                self.messages.append(f"Moved {direction_str}")
            else:
                # Try alternate moves if direct path is blocked
                if dx != 0 and self.is_valid_move(player.x + dx, player.y):
                    player.x += dx
                    action_taken = True
                elif dy != 0 and self.is_valid_move(player.x, player.y + dy):
                    player.y += dy
                    action_taken = True
                else:
                    self.messages.append("That direction is blocked!")

            # Process enemy turns if the player took any action (attack or move)
            if action_taken:
                self.process_enemy_turns()

            return action_taken

        except ValueError as e:
            self.messages.append(str(e))
            return False

    def check_all_enemies_dead(self):
        for entity in self.entities.values():
            if entity.entity_type == 'enemy' and entity.health > 0:
                return False
        return True

    def level_cleared(self):
        if self.check_all_enemies_dead():
            GAME_CONFIG['INITIAL_PLAYER_HEALTH'] += 10
            GAME_CONFIG['PLAYER_BASE_DAMAGE'] += 5
            GAME_CONFIG['PLAYER_HEALTH_REGEN_AFTER_KILL'] += 2

            self.messages.append("All stats increased!")

            try:
                player_id, player = self.get_player()

                health_regained = int(GAME_CONFIG['INITIAL_PLAYER_HEALTH'] * 0.25)
                player.health += health_regained

                self.messages.append(f"You Regained {health_regained} health")
                return True

            except ValueError as e:
                self.messages.append(str(e))
                return False

    def win(self):
        if self.level_cleared() and self.current_level == 3:
            self.messages.append("YOU WIN!")


    # -----------------
    # State Serialization
    # -----------------

    def to_dict(self):
        """Convert the game state to a dictionary for JSON serialization."""
        return {
            'width': self.width,
            'height': self.height,
            'level': self.current_level,
            'messages': self.messages[-5:],
            'walls': self.walls,
            'game_over': self.game_over,
            'combat_this_turn': self.combat_this_turn,
            'entities': {
                str(entity_id): {
                    'x': entity.x,
                    'y': entity.y,
                    'type': entity.entity_type,
                    'health': entity.health,
                    'behavior': entity.behavior
                }
                for entity_id, entity in self.entities.items()
            }
        }