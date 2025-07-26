class FishingGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        
        this.score = 0;
        this.fishCaught = 0;
        
        this.player = {
            x: this.width / 2,
            y: 100,
            rodAngle: 0,
            casting: false,
            power: 0
        };
        
        this.hook = {
            x: this.player.x,
            y: this.player.y + 50,
            targetX: this.player.x,
            targetY: this.player.y + 50,
            moving: false,
            inWater: false
        };
        
        this.fish = [];
        this.particles = [];
        this.waves = [];
        
        this.waterLevel = this.height * 0.4;
        this.time = 0;
        
        this.initWaves();
        this.spawnFish();
        this.setupEventListeners();
        this.gameLoop();
    }
    
    initWaves() {
        for (let i = 0; i < 20; i++) {
            this.waves.push({
                x: (i * this.width) / 20,
                amplitude: Math.random() * 10 + 5,
                frequency: Math.random() * 0.02 + 0.01,
                phase: Math.random() * Math.PI * 2
            });
        }
    }
    
    spawnFish() {
        for (let i = 0; i < 8; i++) {
            this.fish.push({
                x: Math.random() * this.width,
                y: this.waterLevel + 100 + Math.random() * (this.height - this.waterLevel - 200),
                vx: (Math.random() - 0.5) * 3,
                vy: (Math.random() - 0.5) * 1,
                size: Math.random() * 30 + 20,
                color: `hsl(${Math.random() * 60 + 180}, 70%, 50%)`,
                caught: false,
                type: Math.floor(Math.random() * 3)
            });
        }
    }
    
    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => {
            if (!this.hook.moving) {
                this.player.casting = true;
                this.player.power = 0;
            }
        });
        
        this.canvas.addEventListener('mouseup', (e) => {
            if (this.player.casting) {
                this.cast(e);
                this.player.casting = false;
            }
        });
        
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            if (!this.hook.moving) {
                this.player.rodAngle = Math.atan2(mouseY - this.player.y, mouseX - this.player.x);
            }
        });
    }
    
    cast(e) {
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const distance = Math.min(this.player.power * 8, 400);
        const angle = Math.atan2(mouseY - this.player.y, mouseX - this.player.x);
        
        this.hook.targetX = this.player.x + Math.cos(angle) * distance;
        this.hook.targetY = Math.max(this.waterLevel + 50, this.player.y + Math.sin(angle) * distance);
        this.hook.moving = true;
        this.hook.inWater = false;
        
        this.createSplashParticles(this.hook.targetX, this.hook.targetY);
    }
    
    createSplashParticles(x, y) {
        for (let i = 0; i < 15; i++) {
            this.particles.push({
                x: x,
                y: y,
                vx: (Math.random() - 0.5) * 10,
                vy: Math.random() * -8 - 2,
                life: 1,
                decay: 0.02,
                size: Math.random() * 4 + 2,
                color: `rgba(135, 206, 235, ${Math.random() * 0.8 + 0.2})`
            });
        }
    }
    
    updateHook() {
        if (this.hook.moving) {
            const dx = this.hook.targetX - this.hook.x;
            const dy = this.hook.targetY - this.hook.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 5) {
                this.hook.x += dx * 0.15;
                this.hook.y += dy * 0.15;
            } else {
                this.hook.x = this.hook.targetX;
                this.hook.y = this.hook.targetY;
                this.hook.moving = false;
                this.hook.inWater = this.hook.y > this.waterLevel;
                
                if (this.hook.inWater) {
                    this.createSplashParticles(this.hook.x, this.waterLevel);
                }
            }
        }
        
        if (this.hook.inWater && !this.hook.moving) {
            this.hook.y += Math.sin(this.time * 0.05) * 0.5;
            this.checkFishCatch();
        }
    }
    
    checkFishCatch() {
        this.fish.forEach((fish, index) => {
            if (!fish.caught) {
                const dx = fish.x - this.hook.x;
                const dy = fish.y - this.hook.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < fish.size) {
                    fish.caught = true;
                    this.score += fish.size;
                    this.fishCaught++;
                    this.updateUI();
                    
                    this.createCatchParticles(fish.x, fish.y);
                    
                    setTimeout(() => {
                        this.fish[index] = {
                            x: Math.random() * this.width,
                            y: this.waterLevel + 100 + Math.random() * (this.height - this.waterLevel - 200),
                            vx: (Math.random() - 0.5) * 3,
                            vy: (Math.random() - 0.5) * 1,
                            size: Math.random() * 30 + 20,
                            color: `hsl(${Math.random() * 60 + 180}, 70%, 50%)`,
                            caught: false,
                            type: Math.floor(Math.random() * 3)
                        };
                    }, 2000);
                }
            }
        });
    }
    
    createCatchParticles(x, y) {
        for (let i = 0; i < 20; i++) {
            this.particles.push({
                x: x,
                y: y,
                vx: (Math.random() - 0.5) * 15,
                vy: (Math.random() - 0.5) * 15,
                life: 1,
                decay: 0.015,
                size: Math.random() * 6 + 3,
                color: `hsl(${Math.random() * 60 + 30}, 100%, 60%)`
            });
        }
    }
    
    updateFish() {
        this.fish.forEach(fish => {
            if (!fish.caught) {
                fish.x += fish.vx;
                fish.y += fish.vy;
                
                if (fish.x < 0 || fish.x > this.width) fish.vx *= -1;
                if (fish.y < this.waterLevel + 50 || fish.y > this.height - 50) fish.vy *= -1;
                
                if (Math.random() < 0.02) {
                    fish.vx += (Math.random() - 0.5) * 0.5;
                    fish.vy += (Math.random() - 0.5) * 0.3;
                    fish.vx = Math.max(-3, Math.min(3, fish.vx));
                    fish.vy = Math.max(-1, Math.min(1, fish.vy));
                }
            }
        });
    }
    
    updateParticles() {
        this.particles = this.particles.filter(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.vy += 0.3;
            particle.life -= particle.decay;
            return particle.life > 0;
        });
    }
    
    updateUI() {
        document.getElementById('score').textContent = Math.floor(this.score);
        document.getElementById('fish-count').textContent = this.fishCaught;
    }
    
    draw() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        this.drawWater();
        this.drawFish();
        this.drawPlayer();
        this.drawFishingLine();
        this.drawHook();
        this.drawParticles();
        
        if (this.player.casting) {
            this.drawPowerBar();
        }
    }
    
    drawWater() {
        this.ctx.fillStyle = 'rgba(30, 75, 59, 0.3)';
        this.ctx.fillRect(0, this.waterLevel, this.width, this.height - this.waterLevel);
        
        this.ctx.strokeStyle = 'rgba(135, 206, 235, 0.8)';
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        
        for (let i = 0; i < this.waves.length; i++) {
            const wave = this.waves[i];
            const y = this.waterLevel + Math.sin(this.time * wave.frequency + wave.phase) * wave.amplitude;
            
            if (i === 0) {
                this.ctx.moveTo(wave.x, y);
            } else {
                this.ctx.lineTo(wave.x, y);
            }
        }
        this.ctx.stroke();
    }
    
    drawPlayer() {
        this.ctx.save();
        this.ctx.translate(this.player.x, this.player.y);
        
        this.ctx.fillStyle = '#8B4513';
        this.ctx.fillRect(-15, -10, 30, 20);
        
        this.ctx.save();
        this.ctx.rotate(this.player.rodAngle);
        this.ctx.strokeStyle = '#654321';
        this.ctx.lineWidth = 4;
        this.ctx.beginPath();
        this.ctx.moveTo(0, 0);
        this.ctx.lineTo(80, 0);
        this.ctx.stroke();
        this.ctx.restore();
        
        this.ctx.restore();
    }
    
    drawFishingLine() {
        this.ctx.strokeStyle = 'rgba(100, 100, 100, 0.8)';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(
            this.player.x + Math.cos(this.player.rodAngle) * 80,
            this.player.y + Math.sin(this.player.rodAngle) * 80
        );
        this.ctx.lineTo(this.hook.x, this.hook.y);
        this.ctx.stroke();
    }
    
    drawHook() {
        this.ctx.fillStyle = '#C0C0C0';
        this.ctx.beginPath();
        this.ctx.arc(this.hook.x, this.hook.y, 5, 0, Math.PI * 2);
        this.ctx.fill();
        
        if (this.hook.inWater) {
            this.ctx.strokeStyle = 'rgba(135, 206, 235, 0.5)';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(this.hook.x, this.hook.y, 15 + Math.sin(this.time * 0.1) * 3, 0, Math.PI * 2);
            this.ctx.stroke();
        }
    }
    
    drawFish() {
        this.fish.forEach(fish => {
            if (!fish.caught) {
                this.ctx.save();
                this.ctx.translate(fish.x, fish.y);
                
                if (fish.vx < 0) {
                    this.ctx.scale(-1, 1);
                }
                
                this.ctx.fillStyle = fish.color;
                this.ctx.beginPath();
                this.ctx.ellipse(0, 0, fish.size, fish.size * 0.6, 0, 0, Math.PI * 2);
                this.ctx.fill();
                
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                this.ctx.beginPath();
                this.ctx.ellipse(-fish.size * 0.3, -fish.size * 0.2, fish.size * 0.2, fish.size * 0.2, 0, 0, Math.PI * 2);
                this.ctx.fill();
                
                this.ctx.fillStyle = '#000';
                this.ctx.beginPath();
                this.ctx.ellipse(-fish.size * 0.3, -fish.size * 0.2, fish.size * 0.1, fish.size * 0.1, 0, 0, Math.PI * 2);
                this.ctx.fill();
                
                this.ctx.fillStyle = fish.color;
                this.ctx.beginPath();
                this.ctx.moveTo(fish.size * 0.8, 0);
                this.ctx.lineTo(fish.size * 1.3, -fish.size * 0.3);
                this.ctx.lineTo(fish.size * 1.3, fish.size * 0.3);
                this.ctx.closePath();
                this.ctx.fill();
                
                this.ctx.restore();
            }
        });
    }
    
    drawParticles() {
        this.particles.forEach(particle => {
            this.ctx.save();
            this.ctx.globalAlpha = particle.life;
            this.ctx.fillStyle = particle.color;
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();
        });
    }
    
    drawPowerBar() {
        const barWidth = 200;
        const barHeight = 20;
        const x = this.width / 2 - barWidth / 2;
        const y = 50;
        
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        this.ctx.fillRect(x - 5, y - 5, barWidth + 10, barHeight + 10);
        
        this.ctx.fillStyle = '#333';
        this.ctx.fillRect(x, y, barWidth, barHeight);
        
        const powerWidth = (this.player.power / 100) * barWidth;
        const gradient = this.ctx.createLinearGradient(x, y, x + barWidth, y);
        gradient.addColorStop(0, '#00FF00');
        gradient.addColorStop(0.5, '#FFFF00');
        gradient.addColorStop(1, '#FF0000');
        
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(x, y, powerWidth, barHeight);
    }
    
    gameLoop() {
        this.time++;
        
        if (this.player.casting) {
            this.player.power = Math.min(100, this.player.power + 2);
        }
        
        this.updateHook();
        this.updateFish();
        this.updateParticles();
        this.draw();
        
        requestAnimationFrame(() => this.gameLoop());
    }
}

window.addEventListener('load', () => {
    new FishingGame();
});