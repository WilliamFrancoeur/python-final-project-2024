TILE_TYPES = {
    '#': {
        'name': 'wall',
        'blocks_movement': True,
        'blocks_sight': True,
        'sprite': 'wall',
        'variant': 'stone'
    },
    '.': {
        'name': 'floor',
        'blocks_movement': False,
        'blocks_sight': False,
        'sprite': 'floor',
        'variant': 'stone'
    },
    'P': {
        'name': 'player_start',
        'blocks_movement': False,
        'blocks_sight': False,
        'sprite': 'floor',
        'variant': 'stone'
    },
    'E': {
        'name': 'enemy_spawn',
        'blocks_movement': False,
        'blocks_sight': False,
        'sprite': 'floor',
        'variant': 'stone'
    }
}