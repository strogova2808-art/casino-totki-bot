class CasinoApp {
    constructor() {
        this.userData = null;
        this.userBalance = 666;
        this.currentBet = 3;
        this.isSpinning = false;
        this.gamesPlayed = 0;
        this.totalWon = 0;
        this.biggestWin = 0;
        this.winsCount = 0;
        this.gameHistory = [];
        this.selectedDepositAmount = 0;
        this.currentPrize = null;
        this.userId = 1;
        this.stickersLoaded = false;
        this.quickSpinMode = false;
        
        // Правильные призы за 3 одинаковых стикера
        this.prizesConfig = {
    3: { // Ставка 3 звезды - базовые призы
        'bear': { name: 'Мишка', value: 21 },
        'rose': { name: 'Роза', value: 32 },
        'ring': { name: 'Кольцо', value: 129 },
        'rocket': { name: 'Ракета', value: 63 }
    },
    9: { // Ставка 9 звезд - добавляются NFT начального уровня
        'rose': { name: 'Роза', value: 32 },
        'rocket': { name: 'Ракета', value: 63 },
        'candy': { name: 'Candy Cane', value: 357 },
        'b-day': { name: 'B-Day Candle', value: 378 },
        'desk': { name: 'Desk Calendar', value: 315 },
        's-box': { name: 'Snake Box', value: 389 }
    },
    15: { // Ставка 15 звезд - добавляются редкие NFT
        'ring': { name: 'Кольцо', value: 129 },
        'rocket': { name: 'Ракета', value: 63 },
        'candy': { name: 'Candy Cane', value: 357 },
        'b-day': { name: 'B-Day Candle', value: 378 },
        'desk': { name: 'Desk Calendar', value: 315 },
        's-box': { name: 'Snake Box', value: 389 },
        'Tama': { name: 'Tama Gadget', value: 525 },
        'Hypno': { name: 'Hypno Lollipop', value: 525 },
        'Etern': { name: 'Eternal Candle', value: 840 },
        'HePo': { name: 'Hex Pot', value: 735 }
    }
    
};


        // Веса для разных ставок (исправленные шансы)
        this.weights = {
            3: {
                'bear': 30,   // Увеличен шанс
                'rose': 30,   // Увеличен шанс  
                'ring': 20,   // Уменьшен шанс
                'rocket': 20  // Уменьшен шанс
            },
            9: {
                'rose': 25,
                'rocket': 12,
                'candy': 8,   // NFT - маленький шанс
                'b-day': 6,   // NFT - маленький шанс
                'desk': 5,    // NFT - маленький шанс
                's-box': 4    // NFT - маленький шанс
            },
            15: {
                'ring': 15,
                'rocket': 12,
                'candy': 8,
                'b-day': 6,
                'desk': 5,
                's-box': 4,
                'Tama': 3,    // Редкий NFT - очень маленький шанс
                'Hypno': 2,   // Редкий NFT - очень маленький шанс
                'Etern': 1,   // Редкий NFT - минимальный шанс
                'HePo': 1     // Редкий NFT - минимальный шанс
            }
        };

        this.stickerEmojis = {
            'bear': '🧸', 'rose': '🌹', 'ring': '💍', 'rocket': '🚀',
            'candy': '🍬', 'b-day': '🎂', 'desk': '📅', 's-box': '🐍',
            'Tama': '📱', 'Hypno': '🍭', 'Etern': '🕯️', 'HePo': '⚗️'
        };

        this.stickerNames = {
            'bear': 'Мишка', 'rose': 'Роза', 'ring': 'Кольцо', 'rocket': 'Ракета',
            'candy': 'Candy Cane', 'b-day': 'B-Day Candle', 'desk': 'Desk Calendar', 
            's-box': 'Snake Box', 'Tama': 'Tama Gadget', 'Hypno': 'Hypno Lollipop',
            'Etern': 'Eternal Candle', 'HePo': 'Hex Pot'
        };

        this.init();
    }

    async init() {
        await this.initTelegramWebApp();
        await this.preloadStickers();
        this.setupEventListeners();
        
        // ЗАГРУЖАЕМ ДАННЫЕ ИЗ БАЗЫ ПРИ ЗАПУСКЕ
        await this.loadUserDataFromDatabase();
        
        this.updateUI();
        this.selectBet(3);
        this.updateHistory();
        this.setInitialStickers();
    }

    async loadUserDataFromDatabase() {
        console.log('🔄 Загрузка данных пользователя из базы...');
        
        if (window.Telegram && Telegram.WebApp) {
            try {
                // Отправляем запрос на синхронизацию с базой
                const data = {
                    user_id: this.userId,
                    action: 'sync_user_data'
                };
                
                Telegram.WebApp.sendData(JSON.stringify(data));
                console.log('✅ Запрос на синхронизацию отправлен');
            } catch (error) {
                console.error('❌ Ошибка синхронизации с базой:', error);
                // Загружаем из localStorage как fallback
                this.loadUserDataFromLocalStorage();
            }
        } else {
            this.loadUserDataFromLocalStorage();
        }
    }

    loadUserDataFromLocalStorage() {
        const userKey = `casino_user_${this.userId}`;
        const savedData = localStorage.getItem(userKey);
        
        if (savedData) {
            const data = JSON.parse(savedData);
            this.userBalance = data.balance || 666;
            this.gamesPlayed = data.gamesPlayed || 0;
            this.totalWon = data.totalWon || 0;
            this.biggestWin = data.biggestWin || 0;
            this.winsCount = data.winsCount || 0;
            this.gameHistory = data.gameHistory || [];
        }
    }

    async saveUserDataToDatabase() {
        console.log('💾 Сохранение данных в базу...');
        
        if (window.Telegram && Telegram.WebApp) {
            try {
                const data = {
                    user_id: this.userId,
                    action: 'update_balance',
                    balance: this.userBalance,
                    games_played: this.gamesPlayed,
                    total_won: this.totalWon,
                    biggest_win: this.biggestWin,
                    wins_count: this.winsCount
                };
                
                Telegram.WebApp.sendData(JSON.stringify(data));
                console.log('✅ Данные отправлены в базу');
            } catch (error) {
                console.error('❌ Ошибка сохранения в базу:', error);
                // Сохраняем в localStorage как fallback
                this.saveUserDataToLocalStorage();
            }
        } else {
            this.saveUserDataToLocalStorage();
        }
    }

    saveUserDataToLocalStorage() {
        const userKey = `casino_user_${this.userId}`;
        const data = {
            balance: this.userBalance,
            gamesPlayed: this.gamesPlayed,
            totalWon: this.totalWon,
            biggestWin: this.biggestWin,
            winsCount: this.winsCount,
            gameHistory: this.gameHistory,
            userId: this.userId,
            username: this.userData?.username,
            first_name: this.userData?.first_name,
            last_updated: Date.now()
        };
        localStorage.setItem(userKey, JSON.stringify(data));
    }

    async preloadStickers() {
        console.log('🔄 Предзагрузка GIF стикеров...');
        const allStickers = Object.keys(this.weights[15]); // Все стикеры из максимальной ставки
        
        const preloadPromises = allStickers.map(sticker => {
            return new Promise((resolve) => {
                const img = new Image();
                img.src = `stickers/${sticker}.gif`;
                img.onload = () => {
                    console.log(`✅ Стикер ${sticker} загружен`);
                    resolve();
                };
                img.onerror = () => {
                    console.warn(`❌ Ошибка загрузки стикера ${sticker}`);
                    resolve();
                };
            });
        });

        await Promise.all(preloadPromises);
        this.stickersLoaded = true;
        console.log('✅ Все GIF стикеры загружены');
    }

    setInitialStickers() {
        ['bear', 'rose', 'ring'].forEach((sticker, index) => {
            this.updateReelSticker(index + 1, sticker);
        });
    }

    getWeightedRandomSticker(bet) {
        const weights = this.weights[bet];
        const totalWeight = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
        let random = Math.random() * totalWeight;
        
        for (const [sticker, weight] of Object.entries(weights)) {
            random -= weight;
            if (random <= 0) return sticker;
        }
        
        return Object.keys(weights)[0];
    }

    async initTelegramWebApp() {
        if (window.Telegram && Telegram.WebApp) {
            try {
                Telegram.WebApp.ready();
                Telegram.WebApp.expand();
                
                const user = Telegram.WebApp.initDataUnsafe?.user;
                if (user) {
                    this.userData = user;
                    this.updateUserInfo(user);
                    this.userId = user.id;
                    document.getElementById('profileId').textContent = this.userId;
                }
            } catch (error) {
                console.error('Error initializing Telegram WebApp:', error);
                this.setupFallbackData();
            }
        } else {
            this.setupFallbackData();
        }
    }

    updateUserInfo(user) {
        const username = user.username ? `@${user.username}` : (user.first_name || 'Игрок');
        document.getElementById('profileName').textContent = username;
        this.updateUserAvatar(user);
    }

    updateUserAvatar(user) {
        const avatarContainer = document.getElementById('profileAvatar');
        if (user.photo_url) {
            avatarContainer.innerHTML = `<img src="${user.photo_url}" alt="Avatar" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
        } else {
            const colors = [['#7f2b8f', '#c44569'], ['#2b8f8c', '#69c4a4']];
            const colorIndex = (user.id || 0) % colors.length;
            const userInitial = user.first_name ? user.first_name.charAt(0).toUpperCase() : 'U';
            avatarContainer.innerHTML = `<div class="gradient-avatar-large" style="background: linear-gradient(135deg, ${colors[colorIndex][0]}, ${colors[colorIndex][1]})">${userInitial}</div>`;
        }
    }

    setupFallbackData() {
        this.userData = { id: Date.now(), first_name: 'Игрок', username: 'player' };
        this.updateUserInfo(this.userData);
        this.userId = this.userData.id;
        document.getElementById('profileId').textContent = this.userId;
    }

    setupEventListeners() {
        if (window.Telegram && Telegram.WebApp) {
            Telegram.WebApp.onEvent('webAppDataReceived', (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.balance !== undefined) {
                        this.userBalance = data.balance;
                        this.gamesPlayed = data.games_played || 0;
                        this.totalWon = data.total_won || 0;
                        this.biggestWin = data.biggest_win || 0;
                        this.winsCount = data.wins_count || 0;
                        this.updateUI();
                        this.saveUserData();
                    }
                } catch (error) {
                    console.error('Error parsing data from bot:', error);
                }
            });
        }

        // Блокировка масштабирования
        document.addEventListener('gesturestart', function(e) {
            e.preventDefault();
        });
        document.addEventListener('gesturechange', function(e) {
            e.preventDefault();
        });
        document.addEventListener('gestureend', function(e) {
            e.preventDefault();
        });
    }

    updateUI() {
        this.updateBalance();
        this.updateProfileStats();
    }

    updateBalance() {
        document.getElementById('profileBalance').textContent = this.userBalance + ' ⭐';
    }

    updateProfileStats() {
        document.getElementById('statGames').textContent = this.gamesPlayed;
        const winrate = this.gamesPlayed > 0 ? Math.round((this.winsCount / this.gamesPlayed) * 100) : 0;
        document.getElementById('statWinrate').textContent = winrate + '%';
        document.getElementById('statTotalWon').textContent = this.formatNumber(this.totalWon) + ' ⭐';
        document.getElementById('statRecord').textContent = this.formatNumber(this.biggestWin) + ' ⭐';
    }

    updateHistory() {
        const historyList = document.getElementById('historyList');
        if (this.gameHistory.length === 0) {
            historyList.innerHTML = '<div class="history-empty">Пока нет истории игр</div>';
            return;
        }

        historyList.innerHTML = this.gameHistory.slice(-10).reverse().map(game => `
            <div class="history-item ${game.win ? 'history-win' : 'history-loss'}">
                ${game.win ? `
                    <div class="history-prize">
                        <img src="stickers/${game.prizeSticker}.gif" alt="${game.prizeName}" class="history-sticker">
                        <div class="history-prize-info">
                            <div class="history-prize-name">${game.prizeName}</div>
                            <div class="history-prize-value">${game.prizeValue} ⭐</div>
                        </div>
                    </div>
                ` : `
                    <div class="history-loss-info">
                        <div class="history-loss-text">❌ Проигрыш</div>
                        <div class="history-loss-amount">-${game.betAmount} ⭐</div>
                    </div>
                `}
                <div class="history-time">${game.time}</div>
            </div>
        `).join('');
    }

    addToHistory(win, prize = null, betAmount = 0) {
        const now = new Date();
        const time = now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

        const historyItem = { win, time, betAmount };
        if (win && prize) {
            historyItem.prizeName = prize.name;
            historyItem.prizeSticker = prize.sticker;
            historyItem.prizeValue = prize.value;
        }

        this.gameHistory.push(historyItem);
        if (this.gameHistory.length > 50) this.gameHistory = this.gameHistory.slice(-50);
        this.updateHistory();
    }

    selectBet(bet) {
        if (this.isSpinning) return;
        this.currentBet = bet;
        document.querySelectorAll('.bet-option').forEach(option => {
            option.classList.toggle('active', parseInt(option.dataset.bet) === bet);
        });
        document.getElementById('spinAmount').textContent = bet + ' ⭐';
        document.getElementById('quickSpinAmount').textContent = bet + ' ⭐';
    }

    toggleQuickSpin() {
        this.quickSpinMode = !this.quickSpinMode;
        const quickBtn = document.getElementById('quickSpinBtn');
        const spinBtn = document.getElementById('spinBtn');
        const toggleBtn = document.querySelector('.quick-toggle');
        
        if (this.quickSpinMode) {
            quickBtn.style.display = 'flex';
            spinBtn.style.display = 'none';
            toggleBtn.classList.add('active');
            toggleBtn.innerHTML = '⚡ Быстрая крутка (ВКЛ)';
        } else {
            quickBtn.style.display = 'none';
            spinBtn.style.display = 'flex';
            toggleBtn.classList.remove('active');
            toggleBtn.innerHTML = '⚡ Быстрая крутка';
        }
    }

    async spinSlot() {
        if (this.isSpinning) return;
        if (this.userBalance < this.currentBet) {
            this.showNotification('❌ Недостаточно звезд!');
            return;
        }

        this.isSpinning = true;
        this.disableBetSelection(true);
        
        const spinBtn = this.quickSpinMode ? document.getElementById('quickSpinBtn') : document.getElementById('spinBtn');
        spinBtn.disabled = true;

        document.getElementById('resultCombination').style.display = 'none';
        document.getElementById('resultMessage').textContent = '🎰 Крутим...';

        const spinDuration = this.quickSpinMode ? 1000 : 2000;
        const spinResult = await this.animateReels(spinDuration);
        const prize = this.checkWin(spinResult);
        
        // ВЫЧИТАЕМ СТАВКУ И ОБНОВЛЯЕМ БАЛАНС
        this.userBalance -= this.currentBet;
        this.gamesPlayed++;

        if (prize) {
            this.winsCount++;
            this.totalWon += prize.value;
            this.biggestWin = Math.max(this.biggestWin, prize.value);
            this.userBalance += prize.value; // ДОБАВЛЯЕМ ВЫИГРЫШ
            
            document.getElementById('resultMessage').textContent = `🎉 Выигрыш: ${prize.name}!`;
            this.addToHistory(true, prize, this.currentBet);
            this.currentPrize = prize;
            
            setTimeout(() => this.showPrizeModal(prize), 1000);
        } else {
            document.getElementById('resultMessage').textContent = '❌ Попробуйте еще раз!';
            this.addToHistory(false, null, this.currentBet);
        }
        
        this.isSpinning = false;
        spinBtn.disabled = false;
        this.disableBetSelection(false);
        
        // СОХРАНЯЕМ ДАННЫЕ В БАЗУ ПОСЛЕ КАЖДОЙ ИГРЫ
        this.updateUI();
        await this.saveUserDataToDatabase();
    }

    disableBetSelection(disabled) {
        document.querySelectorAll('.bet-option').forEach(option => {
            option.classList.toggle('disabled', disabled);
            option.style.pointerEvents = disabled ? 'none' : 'auto';
        });
    }

    async animateReels(spinDuration = 2000) {
        const reels = [1, 2, 3];
        const stickers = [];

        // Запускаем анимацию вращения
        reels.forEach(reel => {
            const reelElement = document.getElementById(`reel${reel}`);
            reelElement.classList.add('spinning');
            this.animateReelSpinning(reel, spinDuration);
        });

        // Ждем завершения анимации
        await this.sleep(spinDuration);

        // Останавливаем барабаны с взвешенными случайными стикерами
        for (let i = 0; i < reels.length; i++) {
            const reelNumber = reels[i];
            const reelElement = document.getElementById(`reel${reelNumber}`);
            reelElement.classList.remove('spinning');
            
            // Взвешенный случайный стикер
            const sticker = this.getWeightedRandomSticker(this.currentBet);
            stickers.push(sticker);
            this.updateReelSticker(reelNumber, sticker);
            
            // Задержка между остановкой барабанов
            if (i < reels.length - 1) {
                await this.sleep(300);
            }
        }

        return stickers;
    }

    async animateReelSpinning(reelNumber, spinDuration) {
        const changeInterval = 100;
        const changes = spinDuration / changeInterval;
        
        for (let i = 0; i < changes; i++) {
            if (!document.getElementById(`reel${reelNumber}`).classList.contains('spinning')) {
                break;
            }
            
            const availableStickers = Object.keys(this.weights[this.currentBet]);
            const randomSticker = availableStickers[Math.floor(Math.random() * availableStickers.length)];
            this.updateReelStickerQuick(reelNumber, randomSticker);
            await this.sleep(changeInterval);
        }
    }

    updateReelSticker(reelNumber, stickerName) {
        const stickerContainer = document.getElementById(`sticker${reelNumber}`);
        stickerContainer.innerHTML = `<img src="stickers/${stickerName}.gif" alt="${stickerName}" class="sticker-gif">`;
    }

    updateReelStickerQuick(reelNumber, stickerName) {
        const stickerContainer = document.getElementById(`sticker${reelNumber}`);
        stickerContainer.innerHTML = `<img src="stickers/${stickerName}.gif" alt="${stickerName}" class="sticker-gif spinning-emoji">`;
    }

    checkWin(spinResult) {
        // Проверяем, все ли три стикера одинаковые
        const firstSticker = spinResult[0];
        if (spinResult.every(sticker => sticker === firstSticker)) {
            const prizeConfig = this.prizesConfig[this.currentBet][firstSticker];
            if (prizeConfig) {
                return {
                    name: prizeConfig.name,
                    value: prizeConfig.value,
                    sticker: firstSticker
                };
            }
        }
        return null;
    }

    showPrizeModal(prize) {
        document.getElementById('prizeCombination').style.display = 'none';
        document.getElementById('prizeName').textContent = prize.name;
        document.getElementById('prizeValue').textContent = `Стоимость: ${prize.value} ⭐`;

        const prizeSticker = document.getElementById('prizeSticker');
        prizeSticker.innerHTML = `<img src="stickers/${prize.sticker}.gif" alt="${prize.name}" style="width: 120px; height: 120px;">`;

        document.getElementById('prizeModal').style.display = 'block';
        this.createConfetti();
    }

    sellPrize() {
        if (this.currentPrize) {
            const sellPrice = Math.round(this.currentPrize.value * 0.7);
            this.userBalance += sellPrice;
            this.showNotification(`💰 Приз продан за ${sellPrice} ⭐`);
            this.closePrizeModal();
            this.updateUI();
            this.saveUserData();
        }
    }

    withdrawPrize() {
        if (this.currentPrize) {
            this.sendWithdrawToBot(this.currentPrize);
            this.showNotification(`🎁 Запрос на вывод ${this.currentPrize.name} отправлен!`);
            this.closePrizeModal();
        }
    }

    sendWithdrawToBot(prize) {
        if (window.Telegram && Telegram.WebApp) {
            const data = {
                user_id: this.userId,
                action: 'withdraw_prize',
                prize: prize.name,
                value: prize.value,
                sticker: prize.sticker
            };
            Telegram.WebApp.sendData(JSON.stringify(data));
        }
    }

    showSection(section) {
        document.querySelectorAll('.section').forEach(sec => {
            sec.classList.remove('active');
        });
        
        document.getElementById(section + '-section').classList.add('active');
        
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const navItems = document.querySelectorAll('.nav-item');
        const sectionIndex = ['history', 'casino', 'profile'].indexOf(section);
        if (sectionIndex !== -1) {
            navItems[sectionIndex].classList.add('active');
        }
    }

    showDepositModal() {
        this.selectedDepositAmount = 0;
        document.getElementById('selectedDeposit').textContent = 'Выберите сумму для пополнения';
        document.getElementById('confirmDeposit').disabled = true;
        
        document.querySelectorAll('.deposit-option').forEach(option => {
            option.classList.remove('selected');
        });
        
        document.getElementById('depositModal').style.display = 'block';
    }

    closeDepositModal() {
        document.getElementById('depositModal').style.display = 'none';
    }

    selectDeposit(amount) {
        this.selectedDepositAmount = amount;
        
        document.querySelectorAll('.deposit-option').forEach(option => {
            option.classList.remove('selected');
        });
        
        event.currentTarget.classList.add('selected');
        
        document.getElementById('selectedDeposit').textContent = `Выбрано: ${amount} ⭐`;
        document.getElementById('confirmDeposit').disabled = false;
    }

    processDeposit() {
        if (this.selectedDepositAmount > 0) {
            if (window.Telegram && Telegram.WebApp) {
                const data = {
                    user_id: this.userId,
                    action: 'deposit_request',
                    amount: this.selectedDepositAmount
                };
                
                console.log('💰 Отправка запроса на пополнение:', data);
                Telegram.WebApp.sendData(JSON.stringify(data));
                
                this.showNotification(`💰 Запрос на пополнение ${this.selectedDepositAmount} ⭐ отправлен администратору!`);
                this.closeDepositModal();
            } else {
                this.showNotification('❌ Ошибка: WebApp не доступен');
            }
        } else {
            this.showNotification('❌ Выберите сумму для пополнения');
        }
    }

    closePrizeModal() {
        document.getElementById('prizeModal').style.display = 'none';
        this.currentPrize = null;
        // Восстанавливаем отображение комбинации
        document.getElementById('resultCombination').style.display = 'block';
        document.getElementById('prizeCombination').style.display = 'block';
    }

    createConfetti() {
        const confettiContainer = document.querySelector('.confetti');
        confettiContainer.innerHTML = '';
        
        for (let i = 0; i < 25; i++) {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: absolute;
                width: 8px;
                height: 8px;
                background: ${this.getRandomColor()};
                top: -10px;
                left: ${Math.random() * 100}%;
                animation: confettiFall ${1 + Math.random() * 2}s linear forwards;
                border-radius: 2px;
            `;
            confettiContainer.appendChild(confetti);
        }
    }

    getRandomColor() {
        const colors = ['#7f2b8f', '#c44569', '#8b2d4d', '#ff6b6b', '#ffa502', '#00d26a'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-surface);
            color: var(--text-primary);
            padding: 12px 20px;
            border-radius: 12px;
            border-left: 4px solid var(--accent-purple);
            box-shadow: var(--shadow);
            z-index: 1000;
            font-size: 14px;
            font-weight: 600;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Инициализация приложения
const casino = new CasinoApp();