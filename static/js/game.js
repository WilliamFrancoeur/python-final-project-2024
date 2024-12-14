import { AudioManager } from './managers/AudioManager.js';
import { RenderManager } from './managers/RenderManager.js';
import { MessageManager } from './managers/MessageManager.js';
import { UIManager } from './managers/UIManager.js';

export class Game {
    constructor() {
        // Initialize managers
        this.audioManager = new AudioManager();
        this.renderManager = new RenderManager();
        this.messageManager = new MessageManager();
        this.uiManager = new UIManager();

        this.gameState = null;
        this.gameOverlay = document.getElementById('gameOverlay');

        // Bind methods
        this.handleClick = this.handleClick.bind(this);

        // Add reset button handler
        this.resetBtn = document.getElementById('resetLevel');
        this.resetBtn.addEventListener('click', () => this.resetLevel());

        this.nextBtn = document.getElementById('nextLevel');
        this.nextBtn.addEventListener('click', () => this.nextLevel());

        // Initialize game
        this.setupEventListeners();
        this.loadGameState();
    }

    setupEventListeners() {
        this.renderManager.canvas.addEventListener('click', this.handleClick);
    }

    async handleClick(e) {
        console.log("Player clicked")
        const rect = this.renderManager.canvas.getBoundingClientRect();
        const clickX = Math.floor((e.clientX - rect.left) / (this.renderManager.TILE_SIZE * this.renderManager.SCALE));
        const clickY = Math.floor((e.clientY - rect.top) / (this.renderManager.TILE_SIZE * this.renderManager.SCALE));

        try {
            const response = await fetch('/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ x: clickX, y: clickY })
            });

            this.gameState = await response.json();
            this.updateGameState();
        } catch (error) {
            console.error('Error:', error);
        }
    }

    updateGameState() {
        this.messageManager.updateMessages(this.gameState.messages);
        this.uiManager.updateHealthBar(this.gameState.entities);
        this.renderManager.render(this.gameState);

        // Play combat sound if there was combat this turn
        if (this.gameState.combat_this_turn) {
            this.audioManager.playRandomSwing();
        }

        // Handle game over state
        if (this.gameState.game_over) {
            this.gameOverlay.style.display = 'flex';
        } else {
            this.gameOverlay.style.display = 'none';
        }
    }

    async loadGameState() {
        try {
            const response = await fetch('/game_state');
            this.gameState = await response.json();
            this.renderManager.initializeCanvas(this.gameState.width, this.gameState.height);
            this.updateGameState();
        } catch (error) {
            console.error('Error loading game state:', error);
        }
    }

    async resetLevel() {
        try {
            const response = await fetch('/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            this.gameState = await response.json();
            this.updateGameState();
        } catch (error) {
            console.error('Error resetting level:', error);
        }
    }
    async nextLevel() {
        console.log('Next level button clicked');
        try {
            const response = await fetch('/next', {
                method: 'POST',
                headers: {
                    'content-Type': 'application/json'
                }
            });

            this.gameState = await response.json();
            this.updateGameState();
        } catch (error) {
            console.error('Error going to next level:', error);
        }
    }
}