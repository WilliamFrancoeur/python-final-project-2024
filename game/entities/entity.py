from dataclasses import dataclass
from typing import Optional

@dataclass
class Entity:
    x: int
    y: int
    entity_type: str  # 'player', 'enemy'
    health: int
    attack: int
    behavior: Optional[str] = None  # 'chase', 'patrol', etc.