export const TILE_SIZE = 16;    // Base tile size
export const SPACING = 1;       // Space between tiles in unpacked version
export const TOTAL_TILE = TILE_SIZE + SPACING;  // Total space each tile takes up
export const SCALE = 2;         // Scale up the tiny tiles for better visibility

export const SPRITE_MAPPING = {
    player: {
        default: [24 * TOTAL_TILE, 0],
        variants: {
            dead: [0, 14 * TOTAL_TILE],
        }
    },
    enemy: {
        default: [26 * TOTAL_TILE, 0],
        variants: {
            chase: [26 * TOTAL_TILE, 0],
            patrol: [27 * TOTAL_TILE, 0],
            spell_caster: [28 * TOTAL_TILE, 0],
            dead: [0, 15 * TOTAL_TILE]
        }
    },
    floor: {
        default: [0, 0],
        variants: {
            // Try different floor tiles that might have less visible edges
            stone: [1 * TOTAL_TILE, 0],
            dirt: [2 * TOTAL_TILE, 0],
            wood: [3 * TOTAL_TILE, 0],
            // Some other options from the tileset:
            smooth: [4 * TOTAL_TILE, 0],    // Might have less visible edges
            carpet: [5 * TOTAL_TILE, 0],    // Different texture
            grass: [6 * TOTAL_TILE, 0]      // Natural look
        }
    },
    wall: {
        default: [0, TOTAL_TILE],
        variants: {
            stone: [TOTAL_TILE, TOTAL_TILE],
            brick: [2 * TOTAL_TILE, TOTAL_TILE],
            wood: [3 * TOTAL_TILE, TOTAL_TILE]
        }
    }
};