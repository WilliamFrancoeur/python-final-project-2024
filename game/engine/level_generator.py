from typing import Dict, List, Tuple
from ..levels.level_data import LEVEL_LAYOUTS
from ..engine.tile_types import TILE_TYPES
from config import GAME_CONFIG


class Level:
    def __init__(self, layout: str):
        self.tiles: List[List[Dict]] = []
        self.width: int = 0
        self.height: int = 0
        self.player_start: Tuple[int, int] = (0, 0)
        self.enemy_spawns: List[Tuple[int, int]] = []
        self.walls: List[Tuple[int, int]] = []
        self.parse_layout(layout)

    def parse_layout(self, layout: str) -> None:
        """Convert the ASCII layout into a tile grid."""
        # Split the layout into lines and remove empty lines and whitespace
        lines = [line.strip() for line in layout.split('\n') if line.strip()]

        self.height = len(lines)
        self.width = len(lines[0])

        for y, line in enumerate(lines):
            tile_row = []
            for x, char in enumerate(line):
                tile_type = TILE_TYPES.get(char, TILE_TYPES['.'])
                tile_row.append(tile_type.copy())

                # Store coordinates for special tiles
                if char == 'P':
                    self.player_start = (x, y)
                elif char == 'E':
                    self.enemy_spawns.append((x, y))
                elif char == '#':
                    self.walls.append((x, y))

            self.tiles.append(tile_row)

        print(f"Parsed level: {self.width}x{self.height}")
        print(f"Walls: {self.walls}")
        print(f"Player start: {self.player_start}")
        print(f"Enemy spawns: {self.enemy_spawns}")

    def get_enemy_spawn_data(self, current_level: int) -> List[Dict]:
        """Generate enemy data for each spawn point."""
        enemy_types = ['chase', 'patrol', 'spell_caster']
        enemy_data = []

        for i, (x, y) in enumerate(self.enemy_spawns):
            health = (GAME_CONFIG['ENEMY_BASE_HEALTH'] +
                      GAME_CONFIG['ENEMY_HEALTH_SCALING'] * (current_level - 1))
            damage = GAME_CONFIG['ENEMY_BASE_DAMAGE'] * (1 + (current_level - 1) * 0.2)

            enemy_data.append({
                'x': x,
                'y': y,
                'health': health,
                'attack': damage,
                'behavior': enemy_types[i % len(enemy_types)]
            })

        return enemy_data


class LevelGenerator:
    @staticmethod
    def create_level(level_number: int) -> Level:
        """Create a level instance from the level number."""
        layout = LEVEL_LAYOUTS.get(level_number, LEVEL_LAYOUTS[1])
        return Level(layout)

    @staticmethod
    def validate_level(level: Level) -> bool:
        """Validate that a level is properly formed."""
        # Check basic requirements
        if not level.player_start:
            return False
        if not level.enemy_spawns:
            return False

        # Ensure map is rectangular
        if not all(len(row) == level.width for row in level.tiles):
            return False

        # Ensure player start and enemy spawns are not in walls
        if level.player_start in level.walls:
            return False
        if any(spawn in level.walls for spawn in level.enemy_spawns):
            return False

        return True