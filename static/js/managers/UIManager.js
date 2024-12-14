export class UIManager {
    constructor() {
        this.healthBar = document.getElementById('playerHealth');
    }

    updateHealthBar(entities) {
        const player = Object.values(entities).find(e => e.type === 'player');

        if (player) {
            const healthPercent = Math.max(0, Math.min(100, player.health));
            this.healthBar.style.width = `${healthPercent}%`;
            this.healthBar.style.backgroundColor =
                healthPercent > 60 ? '#4CAF50' :
                healthPercent > 30 ? '#FFA500' : '#FF0000';
        }
    }
}