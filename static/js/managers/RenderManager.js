import { TILE_SIZE, SCALE, SPRITE_MAPPING } from '../spriteMapping.js';

export class RenderManager {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.tilesheet = new Image();
        this.tilesLoaded = false;
        this.gameState = null;

        this.TILE_SIZE = TILE_SIZE;
        this.SCALE = SCALE;

        this.loadTilesheet();
    }

    loadTilesheet() {
        this.tilesheet.onload = () => {
            this.tilesLoaded = true;
            // Only render if we have both the tilesheet and game state
            if (this.gameState) {
                this.render(this.gameState);
            }
        };
        this.tilesheet.src = '/static/assets/tilesets/colored.png';
    }

    drawSprite(type, x, y, variant = 'default') {
        if (!this.tilesLoaded) return;

        const spriteInfo = SPRITE_MAPPING[type];
        if (!spriteInfo) return;

        const [srcX, srcY] = variant && spriteInfo.variants?.[variant] || spriteInfo.default;

        this.ctx.drawImage(
            this.tilesheet,
            srcX, srcY,              // Source x, y
            TILE_SIZE, TILE_SIZE,    // Source width, height
            x * TILE_SIZE * SCALE,   // Dest x
            y * TILE_SIZE * SCALE,   // Dest y
            TILE_SIZE * SCALE,       // Dest width
            TILE_SIZE * SCALE        // Dest height
        );
    }

    initializeCanvas(width, height) {
        this.canvas.width = width * TILE_SIZE * SCALE;
        this.canvas.height = height * TILE_SIZE * SCALE;
    }

    render(gameState) {
        if (!gameState) return;

        // Store the game state
        this.gameState = gameState;

        // If tiles aren't loaded yet, return and wait for onload callback
        if (!this.tilesLoaded) return;

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw floor tiles first
        for (let x = 0; x < gameState.width; x++) {
            for (let y = 0; y < gameState.height; y++) {
                this.drawSprite('floor', x, y, 'stone');
            }
        }

        // Draw walls
        if (gameState.walls) {
            for (const [x, y] of gameState.walls) {
                this.drawSprite('wall', x, y, 'stone');
            }
        }


        // Sort entities by type and state to control render order
        const sortedEntities = Object.values(gameState.entities).sort((a, b) => {
            // Dead enemies should be rendered first
            if (a.behavior === 'dead' && b.behavior !== 'dead') return -1;
            if (a.behavior !== 'dead' && b.behavior === 'dead') return 1;
            // Then living enemies
            if (a.type === 'enemy' && b.type === 'player') return -1;
            if (a.type === 'player' && b.type === 'enemy') return 1;
            return 0;
        });

        // First pass: Draw all sprites
        sortedEntities.forEach(entity => {
            this.drawSprite(
                entity.type,
                entity.x,
                entity.y,
                entity.behavior || 'default'
            );
        });

        // Second pass: Draw all health bars on top
        sortedEntities.forEach(entity => {
            this.drawHealthBar(entity);
        });

        this.drawGrid(gameState);
    }

    drawHealthBar(entity) {
        // Don't draw health bar for dead entities
        if (entity.behavior === 'dead') {
            return;
        }

        const healthPercent = entity.health / 100;
        const barWidth = TILE_SIZE * SCALE;
        const barX = entity.x * TILE_SIZE * SCALE;
        const barY = entity.y * TILE_SIZE * SCALE - 4;

        this.ctx.fillStyle = '#FF0000';
        this.ctx.fillRect(barX, barY, barWidth, 3);

        this.ctx.fillStyle = '#00FF00';
        this.ctx.fillRect(barX, barY, barWidth * healthPercent, 3);
    }

    drawGrid(gameState) {
        this.ctx.strokeStyle = 'rgba(50, 50, 50, 0.5)';
        this.ctx.lineWidth = 1;

        // Vertical lines
        for (let x = 0; x <= gameState.width; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * TILE_SIZE * SCALE, 0);
            this.ctx.lineTo(x * TILE_SIZE * SCALE, this.canvas.height);
            this.ctx.stroke();
        }

        // Horizontal lines
        for (let y = 0; y <= gameState.height; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * TILE_SIZE * SCALE);
            this.ctx.lineTo(this.canvas.width, y * TILE_SIZE * SCALE);
            this.ctx.stroke();
        }
    }
}