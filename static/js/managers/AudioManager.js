export class AudioManager {
    constructor() {
        this.backgroundMusic = document.getElementById('backgroundMusic');
        this.toggleMusicBtn = document.getElementById('toggleMusic');
        this.volumeSlider = document.getElementById('volumeSlider');
        this.hasStartedOnce = false;

        // Initialize swing sounds array
        this.swingSounds = [
            new Audio('/static/assets/sfx/swing1.wav'),
            new Audio('/static/assets/sfx/swing2.wav'),
            new Audio('/static/assets/sfx/swing3.wav')
        ];

        // Set initial volume for all swing sounds
        this.swingSounds.forEach(sound => {
            sound.volume = this.volumeSlider.value * 0.7; // Slightly quieter than music
        });

        // Set initial state
        this.toggleMusicBtn.textContent = 'Play Music';
        this.setupAudio();
    }

    setupAudio() {
        // Set music to loop
        this.backgroundMusic.loop = true;
        this.backgroundMusic.volume = this.volumeSlider.value;

        // Add event listeners
        this.toggleMusicBtn.addEventListener('click', () => this.toggleMusic());
        this.volumeSlider.addEventListener('input', (e) => this.handleVolumeChange(e));
    }

    async toggleMusic() {
        if (this.backgroundMusic.paused) {
            try {
                // If this is the first time playing, set a random start time
                if (!this.hasStartedOnce) {
                    const duration = this.backgroundMusic.duration;
                    if (duration) {
                        // Start at a random point in the first 80% of the song
                        const randomTime = Math.random() * (duration * 0.8);
                        this.backgroundMusic.currentTime = randomTime;
                        this.hasStartedOnce = true;
                    }
                }
                // Play will resume from current position if not first time
                await this.backgroundMusic.play();
                this.toggleMusicBtn.textContent = 'Pause Music';
            } catch (error) {
                console.error('Playback failed:', error);
                alert('Failed to play audio: ' + error.message);
            }
        } else {
            // Pause will maintain current position
            this.backgroundMusic.pause();
            this.toggleMusicBtn.textContent = 'Play Music';
        }
    }

    handleVolumeChange(e) {
        const volume = e.target.value;
        this.backgroundMusic.volume = volume;
        this.swingSounds.forEach(sound => {
            sound.volume = volume * 0.7;
        });
    }

    playRandomSwing() {
        const randomIndex = Math.floor(Math.random() * this.swingSounds.length);
        const sound = this.swingSounds[randomIndex];
        // Reset the sound to start if it's already playing
        sound.currentTime = 0;
        sound.play().catch(error => {
            console.error('Error playing swing sound:', error);
        });
    }
}