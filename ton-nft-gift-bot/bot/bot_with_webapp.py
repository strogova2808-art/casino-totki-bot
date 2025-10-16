import os
import logging
import sqlite3
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "8373706621:AAFTOCrsNuSuov9pBzj1C1xk7vvC3zo01Nk"
WEBAPP_URL = "https://fantastic-marigold-515e07.netlify.app"
ADMIN_ID = 1376689155

# Ссылки на маркетплейсы
MARKETPLACE_LINKS = {
    'portal': 'https://t.me/portals/market?startapp=68k7zv',
    'mrkt': 'https://t.me/mrkt/app?startapp=1376689155',
    'virus': 'https://t.me/virus_play_bot/app?startapp=roulette_inviteCodeNyzVY2nYykGxC8Lx'
}


class CasinoBot:
    def __init__(self, token: str):
        self.token = token
        self.application = None
        self.init_database()
        self.setup_application()

    def get_db_connection(self):
        """Получить соединение с базой данных"""
        try:
            os.makedirs('bot', exist_ok=True)
            conn = sqlite3.connect('bot/casino.db', check_same_thread=False, timeout=30)
            conn.execute("PRAGMA journal_mode=WAL")
            return conn
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к базе: {e}")
            return None

    def init_database(self):
        """Инициализация базы данных SQLite"""
        try:
            conn = self.get_db_connection()
            if conn is None:
                return

            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    balance INTEGER DEFAULT 666,
                    games_played INTEGER DEFAULT 0,
                    total_won INTEGER DEFAULT 0,
                    biggest_win INTEGER DEFAULT 0,
                    wins_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount INTEGER,
                    type TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("✅ База данных casino.db успешно инициализирована")

        except Exception as e:
            logger.error(f"❌ Ошибка инициализации базы данных: {e}")

    def setup_application(self):
        """Настройка приложения и обработчиков"""
        try:
            self.application = Application.builder().token(self.token).build()

            # Добавляем обработчики команд
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("app", self.app_command))
            self.application.add_handler(CommandHandler("casino", self.casino_command))
            self.application.add_handler(CommandHandler("play", self.play_command))
            self.application.add_handler(CommandHandler("admin", self.admin_command))
            self.application.add_handler(CommandHandler("addstars", self.add_stars_command))
            self.application.add_handler(CommandHandler("userinfo", self.user_info_command))
            self.application.add_handler(CommandHandler("topusers", self.top_users_command))
            self.application.add_handler(CallbackQueryHandler(self.button_handler))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

            logger.info("✅ Обработчики команд настроены")

        except Exception as e:
            logger.error(f"❌ Ошибка настройки приложения: {e}")

    def get_user_data_from_db(self, user_id):
        """Получить данные пользователя из базы"""
        try:
            conn = self.get_db_connection()
            if conn is None:
                return None

            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'user_id': result[0],
                    'username': result[1],
                    'first_name': result[2],
                    'balance': result[3],
                    'games_played': result[4],
                    'total_won': result[5],
                    'biggest_win': result[6],
                    'wins_count': result[7],
                    'created_at': result[8]
                }
            return None

        except Exception as e:
            logger.error(f"❌ Ошибка получения данных пользователя из базы: {e}")
            return None

    def update_user_data_in_db(self, user_data):
        """Обновить данные пользователя в базе"""
        try:
            conn = self.get_db_connection()
            if conn is None:
                return False

            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET 
                balance = ?, 
                games_played = ?, 
                total_won = ?, 
                biggest_win = ?, 
                wins_count = ? 
                WHERE user_id = ?
            ''', (
                user_data['balance'],
                user_data['games_played'],
                user_data['total_won'],
                user_data['biggest_win'],
                user_data['wins_count'],
                user_data['user_id']
            ))
            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка обновления данных пользователя в базе: {e}")
            return False

    def create_user_in_db(self, user_id, username, first_name):
        """Создать нового пользователя в базе"""
        try:
            conn = self.get_db_connection()
            if conn is None:
                return False

            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (user_id, username, first_name, balance) VALUES (?, ?, ?, ?)',
                (user_id, username, first_name, 666)
            )
            conn.commit()
            conn.close()
            logger.info(f"👤 Создан новый пользователь в базе: {first_name} (ID: {user_id})")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка создания пользователя в базе: {e}")
            return False

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()

        if query.data == "admin_panel":
            if query.from_user.id == ADMIN_ID:
                await self.show_admin_panel(query)
            else:
                await query.message.reply_text("❌ У вас нет прав доступа к админ-панели.")

    async def show_admin_panel(self, query):
        """Показать панель администратора"""
        try:
            conn = self.get_db_connection()
            if conn is None:
                await query.message.reply_text("❌ Ошибка подключения к базе данных")
                return

            cursor = conn.cursor()

            cursor.execute('''
                SELECT COUNT(*) as total_users, 
                       SUM(balance) as total_balance,
                       SUM(games_played) as total_games,
                       SUM(total_won) as total_won
                FROM users
            ''')
            stats = cursor.fetchone()

            cursor.execute('SELECT COUNT(*) FROM transactions WHERE status = "pending"')
            pending_deposits = cursor.fetchone()[0]

            conn.close()

            admin_text = (
                f"👑 <b>Панель администратора</b>\n\n"
                f"👥 Всего пользователей: <b>{stats[0]}</b>\n"
                f"💰 Общий баланс: <b>{stats[1] or 0} ⭐</b>\n"
                f"🎰 Сыграно игр: <b>{stats[2] or 0}</b>\n"
                f"🏆 Общий выигрыш: <b>{stats[3] or 0} ⭐</b>\n"
                f"⏳ Ожидают пополнения: <b>{pending_deposits}</b>\n\n"
                "💎 <b>Команды админа:</b>\n"
                "<code>/addstars user_id amount</code> - добавить звезды\n"
                "<code>/userinfo user_id</code> - информация о пользователе\n"
                "<code>/topusers</code> - топ пользователей\n"
            )

            keyboard = [
                [InlineKeyboardButton("🔄 Обновить статистику", callback_data="admin_panel")],
                [InlineKeyboardButton("📊 Топ пользователей", callback_data="show_top_users")]
            ]

            await query.edit_message_text(
                admin_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"❌ Ошибка показа админ-панели: {e}")

    async def handle_webapp_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка данных из WebApp"""
        try:
            user = update.effective_user
            webapp_data = update.effective_message.web_app_data

            logger.info(f"📱 Получены данные от WebApp от пользователя {user.first_name}: {webapp_data.data}")

            if webapp_data:
                data = json.loads(webapp_data.data)
                action = data.get('action')

                logger.info(f"🔧 Action: {action}, Data: {data}")

                if action == 'sync_user_data':
                    # СИНХРОНИЗАЦИЯ ДАННЫХ С БАЗОЙ
                    user_id = data.get('user_id')

                    # Получаем данные из базы
                    db_user_data = self.get_user_data_from_db(user_id)

                    if db_user_data:
                        # Отправляем данные обратно в WebApp
                        await update.message.reply_text(
                            f"✅ Данные синхронизированы с базой!\n"
                            f"💰 Баланс: {db_user_data['balance']} ⭐\n"
                            f"🎰 Игр сыграно: {db_user_data['games_played']}",
                            parse_mode='HTML'
                        )
                    else:
                        # Создаем нового пользователя
                        self.create_user_in_db(
                            user_id,
                            user.username or "Без username",
                            user.first_name or "Игрок"
                        )
                        await update.message.reply_text("✅ Новый пользователь создан в базе!")

                elif action == 'update_balance':
                    # ОБНОВЛЯЕМ ДАННЫЕ В БАЗЕ
                    user_id = data.get('user_id')
                    balance = data.get('balance', 0)
                    games_played = data.get('games_played', 0)
                    total_won = data.get('total_won', 0)
                    biggest_win = data.get('biggest_win', 0)
                    wins_count = data.get('wins_count', 0)

                    user_data = {
                        'user_id': user_id,
                        'balance': balance,
                        'games_played': games_played,
                        'total_won': total_won,
                        'biggest_win': biggest_win,
                        'wins_count': wins_count
                    }

                    success = self.update_user_data_in_db(user_data)

                    if success:
                        logger.info(f"📊 Данные пользователя {user.first_name} обновлены в базе: баланс={balance}")
                        await update.message.reply_text("✅ Данные успешно сохранены в базе!")
                    else:
                        logger.error("❌ Не удалось обновить данные в базе")
                        await update.message.reply_text("❌ Ошибка сохранения данных в базе")

                elif action == 'deposit_request':
                    amount = data.get('amount', 0)
                    user_id = data.get('user_id')

                    logger.info(f"💰 Запрос на пополнение: user_id={user_id}, amount={amount}")

                    # Добавляем транзакцию в базу
                    conn = self.get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            'INSERT INTO transactions (user_id, amount, type, status) VALUES (?, ?, ?, ?)',
                            (user_id, amount, 'deposit', 'pending')
                        )
                        conn.commit()
                        conn.close()

                    # Уведомляем админа
                    admin_text = (
                        f"💰 <b>ЗАПРОС НА ПОПОЛНЕНИЕ</b>\n\n"
                        f"👤 Пользователь: {user.first_name}\n"
                        f"🆔 ID: <code>{user_id}</code>\n"
                        f"📛 Username: @{user.username or 'нет'}\n"
                        f"💎 Сумма: {amount} ⭐\n\n"
                        f"Для пополнения используйте команду:\n"
                        f"<code>/addstars {user_id} {amount}</code>"
                    )

                    await context.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=admin_text,
                        parse_mode='HTML'
                    )

                    # Подтверждаем пользователю
                    await update.message.reply_text(
                        f"✅ <b>Запрос на пополнение отправлен!</b>\n\n"
                        f"💎 Сумма: {amount} ⭐\n"
                        f"👤 Ваш ID: {user_id}\n\n"
                        f"Администратор получил уведомление и пополнит ваш баланс в ближайшее время!",
                        parse_mode='HTML'
                    )

                    logger.info(f"💰 Запрос на пополнение от {user.first_name} (ID: {user_id}): {amount} ⭐")

        except Exception as e:
            logger.error(f"❌ Ошибка обработки данных WebApp: {e}")
            await update.message.reply_text("❌ Ошибка при обработке запроса")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        try:
            user = update.effective_user
            logger.info(f"🎯 Команда /start от пользователя: {user.first_name} (ID: {user.id})")

            # Получаем или создаем пользователя в базе
            user_data = self.get_user_data_from_db(user.id)
            if not user_data:
                self.create_user_in_db(
                    user.id,
                    user.username or "Без username",
                    user.first_name or "Игрок"
                )
                user_data = self.get_user_data_from_db(user.id)

            balance = user_data['balance'] if user_data else 666

            welcome_text = (
                f"🎰 <b>Добро пожаловать в CASINO Totki, {user.first_name}!</b>\n\n"
                f"💰 <b>Ваш баланс:</b> {balance} ⭐\n"
                f"🆔 <b>ID игрока:</b> {user.id}\n\n"
                "🎯 <b>Выигрывай крутые призы!</b>\n\n"
                "👇 <i>Нажми кнопку ниже чтобы начать играть</i>"
            )

            keyboard = [
                [InlineKeyboardButton("🎰 Играть в CASINO Totki", web_app=WebAppInfo(url=WEBAPP_URL))],
                [
                    InlineKeyboardButton("🌐 Portal", url=MARKETPLACE_LINKS['portal']),
                    InlineKeyboardButton("🛍️ MRKT", url=MARKETPLACE_LINKS['mrkt'])
                ],
                [InlineKeyboardButton("🦠 Virus", url=MARKETPLACE_LINKS['virus'])]
            ]

            if user.id == ADMIN_ID:
                keyboard.append([InlineKeyboardButton("👑 Панель админа", callback_data="admin_panel")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"❌ Ошибка в команде /start: {e}")
            await update.message.reply_text("❌ Произошла ошибка при запуске бота.")

    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Панель администратора"""
        try:
            user = update.effective_user

            if user.id != ADMIN_ID:
                await update.message.reply_text("❌ У вас нет прав доступа к этой команде.")
                return

            conn = self.get_db_connection()
            if conn is None:
                await update.message.reply_text("❌ Ошибка подключения к базе данных")
                return

            cursor = conn.cursor()

            cursor.execute('''
                SELECT COUNT(*) as total_users, 
                       SUM(balance) as total_balance,
                       SUM(games_played) as total_games,
                       SUM(total_won) as total_won
                FROM users
            ''')
            stats = cursor.fetchone()

            cursor.execute('SELECT COUNT(*) FROM transactions WHERE status = "pending"')
            pending_deposits = cursor.fetchone()[0]

            conn.close()

            admin_text = (
                f"👑 <b>Панель администратора</b>\n\n"
                f"👥 Всего пользователей: <b>{stats[0]}</b>\n"
                f"💰 Общий баланс: <b>{stats[1] or 0} ⭐</b>\n"
                f"🎰 Сыграно игр: <b>{stats[2] or 0}</b>\n"
                f"🏆 Общий выигрыш: <b>{stats[3] or 0} ⭐</b>\n"
                f"⏳ Ожидают пополнения: <b>{pending_deposits}</b>\n\n"
                "💎 <b>Команды админа:</b>\n"
                "<code>/addstars user_id amount</code> - добавить звезды\n"
                "<code>/userinfo user_id</code> - информация о пользователе\n"
                "<code>/topusers</code> - топ пользователей\n"
            )

            keyboard = [
                [InlineKeyboardButton("🔄 Обновить статистику", callback_data="admin_panel")],
                [InlineKeyboardButton("📊 Топ пользователей", callback_data="show_top_users")]
            ]

            await update.message.reply_text(
                admin_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"❌ Ошибка в команде /admin: {e}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        try:
            # ВАЖНО: Сначала проверяем WebApp данные
            if update.message and update.message.web_app_data:
                await self.handle_webapp_data(update, context)
                return

            user = update.effective_user
            text = update.message.text

            # Проверяем команды админа
            if user.id == ADMIN_ID:
                if text.startswith('/addstars'):
                    await self.handle_add_stars(update, context)
                elif text.startswith('/userinfo'):
                    await self.handle_user_info(update, context)
                elif text.startswith('/topusers'):
                    await self.handle_top_users(update, context)

        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")

    async def add_stars_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /addstars"""
        await self.handle_add_stars(update, context)

    async def user_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /userinfo"""
        await self.handle_user_info(update, context)

    async def top_users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /topusers"""
        await self.handle_top_users(update, context)

    async def handle_add_stars(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление звезд пользователю"""
        try:
            parts = update.message.text.split()
            if len(parts) != 3:
                await update.message.reply_text(
                    "❌ Использование: /addstars user_id amount\n"
                    "Пример: /addstars 123456789 100"
                )
                return

            user_id = int(parts[1])
            amount = int(parts[2])

            # Получаем текущие данные пользователя
            user_data = self.get_user_data_from_db(user_id)
            if not user_data:
                await update.message.reply_text("❌ Пользователь не найден")
                return

            current_balance = user_data['balance']
            new_balance = current_balance + amount

            # Обновляем баланс в базе
            user_data['balance'] = new_balance
            success = self.update_user_data_in_db(user_data)

            if success:
                # Отмечаем транзакции как выполненные
                conn = self.get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'UPDATE transactions SET status = "completed" WHERE user_id = ? AND status = "pending"',
                        (user_id,)
                    )
                    conn.commit()
                    conn.close()

                await update.message.reply_text(
                    f"✅ Баланс пользователя {user_data['first_name']} (ID: {user_id}) обновлен!\n"
                    f"💰 Было: {current_balance} ⭐\n"
                    f"💰 Стало: {new_balance} ⭐\n"
                    f"📈 Добавлено: +{amount} ⭐"
                )

                logger.info(f"💰 Админ добавил {amount} ⭐ пользователю {user_data['first_name']} (ID: {user_id})")
            else:
                await update.message.reply_text("❌ Ошибка обновления баланса")

        except ValueError:
            await update.message.reply_text("❌ Неверный формат. Используйте: /addstars user_id amount")
        except Exception as e:
            logger.error(f"❌ Ошибка добавления звезд: {e}")
            await update.message.reply_text("❌ Ошибка при добавлении звезд")

    async def handle_user_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Информация о пользователе"""
        try:
            parts = update.message.text.split()
            if len(parts) != 2:
                await update.message.reply_text("❌ Использование: /userinfo user_id")
                return

            user_id = int(parts[1])
            user_data = self.get_user_data_from_db(user_id)

            if not user_data:
                await update.message.reply_text("❌ Пользователь не найден")
                return

            user_info = (
                f"👤 <b>Информация о пользователе</b>\n\n"
                f"🆔 ID: <code>{user_data['user_id']}</code>\n"
                f"👤 Имя: <b>{user_data['first_name']}</b>\n"
                f"📛 Username: @{user_data['username'] or 'нет'}\n"
                f"💰 Баланс: <b>{user_data['balance']} ⭐</b>\n"
                f"🎰 Сыграно игр: <b>{user_data['games_played']}</b>\n"
                f"🏆 Выиграно: <b>{user_data['total_won']} ⭐</b>\n"
                f"📈 Рекорд: <b>{user_data['biggest_win']} ⭐</b>\n"
                f"🎯 Побед: <b>{user_data['wins_count']}</b>\n"
                f"📅 Регистрация: <b>{user_data['created_at']}</b>"
            )

            await update.message.reply_text(user_info, parse_mode='HTML')

        except ValueError:
            await update.message.reply_text("❌ Неверный формат. Используйте: /userinfo user_id")
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о пользователе: {e}")

    async def handle_top_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Топ пользователей по балансу"""
        try:
            conn = self.get_db_connection()
            if conn is None:
                await update.message.reply_text("❌ Ошибка подключения к базе данных")
                return

            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, first_name, username, balance, total_won 
                FROM users 
                ORDER BY balance DESC 
                LIMIT 10
            ''')
            top_users = cursor.fetchall()
            conn.close()

            if not top_users:
                await update.message.reply_text("📊 Пока нет пользователей")
                return

            top_text = "🏆 <b>Топ пользователей по балансу</b>\n\n"

            for i, (user_id, first_name, username, balance, total_won) in enumerate(top_users, 1):
                username_display = f"@{username}" if username else "без username"
                top_text += (
                    f"{i}. <b>{first_name}</b> ({username_display})\n"
                    f"   💰 Баланс: <b>{balance} ⭐</b>\n"
                    f"   🏆 Выиграно: <b>{total_won} ⭐</b>\n\n"
                )

            await update.message.reply_text(top_text, parse_mode='HTML')

        except Exception as e:
            logger.error(f"❌ Ошибка получения топа пользователей: {e}")

    async def app_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /app - прямой запуск WebApp"""
        try:
            user = update.effective_user
            user_data = self.get_user_data_from_db(user.id)
            balance = user_data['balance'] if user_data else 666

            keyboard = [
                [InlineKeyboardButton("🎰 ЗАПУСТИТЬ CASINO TOTKI", web_app=WebAppInfo(url=WEBAPP_URL))],
                [
                    InlineKeyboardButton("🌐 Portal", url=MARKETPLACE_LINKS['portal']),
                    InlineKeyboardButton("🛍️ MRKT", url=MARKETPLACE_LINKS['mrkt'])
                ],
                [InlineKeyboardButton("🦠 Virus", url=MARKETPLACE_LINKS['virus'])]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"🎰 <b>Прямой запуск CASINO Totki</b>\n\n"
                f"💰 <b>Твой баланс:</b> {balance} ⭐\n\n"
                "👇 <i>Жми кнопку и погрузись в мир азарта!</i>",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"❌ Ошибка в команде /app: {e}")

    async def casino_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /casino - информация о казино"""
        try:
            user = update.effective_user
            user_data = self.get_user_data_from_db(user.id)
            balance = user_data['balance'] if user_data else 666

            casino_info = (
                f"🎰 <b>CASINO TOTKI - Игровые автоматы</b>\n\n"
                f"💰 <b>Твой баланс:</b> {balance} ⭐\n\n"
                "🛍️ <b>Топ маркетплейсы:</b>\n"
                "• <b>Portal</b> - покупай и продавай NFT\n"
                "• <b>MRKT</b> - эксклюзивные коллекции\n"
                "• <b>Virus</b> - ломай блоки майна и выбивай крутые NFT!\n\n"
                "👇 <i>Начинай играть прямо сейчас!</i>"
            )

            keyboard = [
                [InlineKeyboardButton("🎰 НАЧАТЬ ИГРАТЬ", web_app=WebAppInfo(url=WEBAPP_URL))],
                [
                    InlineKeyboardButton("🌐 Portal", url=MARKETPLACE_LINKS['portal']),
                    InlineKeyboardButton("🛍️ MRKT", url=MARKETPLACE_LINKS['mrkt']),
                    InlineKeyboardButton("🦠 Virus", url=MARKETPLACE_LINKS['virus'])
                ]
            ]

            await update.message.reply_text(
                casino_info,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"❌ Ошибка в команде /casino: {e}")

    async def play_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /play - быстрый старт игры"""
        try:
            user = update.effective_user
            user_data = self.get_user_data_from_db(user.id)
            balance = user_data['balance'] if user_data else 666

            quick_start = (
                f"🎰 <b>Быстрый старт игры!</b>\n\n"
                f"💰 <b>Баланс:</b> {balance} ⭐\n\n"
                "🚀 <b>Готов к победам?</b>\n"
                "👇 <i>Жми кнопку и удача будет на твоей стороне!</i>"
            )

            keyboard = [
                [InlineKeyboardButton("🎰 КРУТИТЬ БАРАБАНЫ!", web_app=WebAppInfo(url=WEBAPP_URL))],
                [
                    InlineKeyboardButton("🌐 Portal", url=MARKETPLACE_LINKS['portal']),
                    InlineKeyboardButton("🛍️ MRKT", url=MARKETPLACE_LINKS['mrkt'])
                ]
            ]

            await update.message.reply_text(
                quick_start,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"❌ Ошибка в команде /play: {e}")


def main():
    """Главная функция запуска бота"""
    print("🎰 ЗАПУСК CASINO TOTKI BOT...")
    print("=" * 50)

    bot = None
    try:
        bot = CasinoBot(BOT_TOKEN)

        if bot.application is None:
            print("❌ Не удалось инициализировать бота")
            return

        print("✅ Бот успешно инициализирован!")
        print(f"🌐 WebApp URL: {WEBAPP_URL}")
        print(f"👑 Admin ID: {ADMIN_ID}")
        print("📱 Доступные команды:")
        print("   /start - Начать работу с ботом")
        print("   /app   - Прямой запуск казино")
        print("   /casino - Информация о казино")
        print("   /play  - Быстрый старт игры")
        print("   /admin - Панель администратора")
        print("   /addstars - Добавить звезды (админ)")
        print("   /userinfo - Информация о пользователе (админ)")
        print("   /topusers - Топ пользователей (админ)")
        print("=" * 50)
        print("🔄 Бот запущен и ожидает сообщений...")

        bot.application.run_polling()

    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка запуска бота: {e}")
    finally:
        print("🎰 Бот завершил работу")


if __name__ == '__main__':
    main()