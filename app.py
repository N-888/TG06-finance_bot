# Импортируем asyncio, чтобы запускать асинхронного Telegram-бота.
import asyncio

# Импортируем html, чтобы безопасно показывать пользовательский текст в HTML-сообщениях.
import html

# Импортируем logging, чтобы видеть рабочие сообщения и ошибки в консоли.
import logging

# Импортируем os, чтобы читать переменные окружения из файла .env.
import os

# Импортируем random, чтобы случайно выбирать совет по экономии.
import random

# Импортируем sqlite3, чтобы хранить данные пользователей в локальной базе данных SQLite.
import sqlite3

# Импортируем Path, чтобы удобно работать с путями к файлам проекта.
from pathlib import Path

# Импортируем aiohttp, чтобы асинхронно получать курс валют через API.
import aiohttp

# Импортируем load_dotenv, чтобы загрузить токены и ключи из файла .env.
from dotenv import load_dotenv

# Импортируем основные классы aiogram для создания бота, диспетчера и фильтров.
from aiogram import Bot, Dispatcher, F

# Импортируем настройки по умолчанию для бота.
from aiogram.client.default import DefaultBotProperties

# Импортируем ParseMode, чтобы красиво форматировать сообщения через HTML.
from aiogram.enums import ParseMode

# Импортируем фильтр команд, чтобы обрабатывать /start, /help, /menu и /cancel.
from aiogram.filters import Command

# Импортируем контекст FSM, чтобы по шагам собирать данные пользователя.
from aiogram.fsm.context import FSMContext

# Импортируем классы состояний FSM.
from aiogram.fsm.state import State, StatesGroup

# Импортируем хранилище состояний в памяти.
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем классы клавиатуры, кнопок, сообщений и команд Telegram.
from aiogram.types import BotCommand, KeyboardButton, Message, ReplyKeyboardMarkup


# Получаем путь к папке, в которой находится текущий файл app.py.
BASE_DIR = Path(__file__).resolve().parent

# Формируем полный путь к файлу .env.
ENV_PATH = BASE_DIR / ".env"

# Загружаем переменные окружения из файла .env.
load_dotenv(ENV_PATH)

# Получаем токен Telegram-бота из переменных окружения и убираем лишние пробелы.
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Получаем ключ API сервиса курсов валют и тоже убираем лишние пробелы.
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY", "").strip()

# Проверяем, указан ли токен Telegram-бота.
if not BOT_TOKEN:
    # Если токен не указан, останавливаем программу с понятным текстом ошибки.
    raise ValueError("Не найден BOT_TOKEN. Создайте файл .env и добавьте туда токен бота.")

# Проверяем, указан ли ключ сервиса курсов валют.
if not EXCHANGE_RATE_API_KEY:
    # Если ключ не указан, останавливаем программу с понятным текстом ошибки.
    raise ValueError("Не найден EXCHANGE_RATE_API_KEY. Создайте файл .env и добавьте туда ключ сервиса валют.")

# Настраиваем логирование, чтобы видеть события работы бота.
logging.basicConfig(
    # Указываем уровень логирования INFO, чтобы показывались основные рабочие сообщения.
    level=logging.INFO,
    # Делаем формат логов более понятным и читаемым.
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# Создаём объект бота и сразу включаем HTML-разметку по умолчанию.
bot = Bot(
    # Передаём токен Telegram-бота.
    token=BOT_TOKEN,
    # Указываем настройки по умолчанию для всех сообщений бота.
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

# Создаём диспетчер и подключаем к нему хранилище состояний в памяти.
dp = Dispatcher(storage=MemoryStorage())


# Создаём красивые тексты кнопок главного меню.
BTN_REGISTER = "📝 Регистрация в телеграм боте"
BTN_RATES = "💱 Курс валют"
BTN_TIPS = "💡 Советы по экономии"
BTN_FINANCES = "📊 Личные финансы"

# Создаём множества допустимых текстов, чтобы бот понимал и кнопки с эмодзи, и обычный текст без эмодзи.
REGISTER_TEXTS = {BTN_REGISTER, "Регистрация в телеграм боте"}
RATES_TEXTS = {BTN_RATES, "Курс валют"}
TIPS_TEXTS = {BTN_TIPS, "Советы по экономии"}
FINANCES_TEXTS = {BTN_FINANCES, "Личные финансы"}

# Создаём кнопку регистрации.
button_registration = KeyboardButton(text=BTN_REGISTER)

# Создаём кнопку курса валют.
button_exchange_rates = KeyboardButton(text=BTN_RATES)

# Создаём кнопку советов по экономии.
button_tips = KeyboardButton(text=BTN_TIPS)

# Создаём кнопку личных финансов.
button_finances = KeyboardButton(text=BTN_FINANCES)

# Собираем нижнюю клавиатуру Telegram из двух рядов кнопок.
keyboard = ReplyKeyboardMarkup(
    # Передаём кнопки построчно.
    keyboard=[
        [button_registration, button_exchange_rates],
        [button_tips, button_finances],
    ],
    # Разрешаем Telegram сделать клавиатуру компактнее.
    resize_keyboard=True,
    # Добавляем подсказку в поле ввода.
    input_field_placeholder="Выберите нужный раздел…",
)

# Формируем путь к базе данных SQLite.
DB_PATH = BASE_DIR / "user.db"

# Открываем соединение с базой данных SQLite.
conn = sqlite3.connect(DB_PATH)

# Получаем курсор, через который будем выполнять SQL-запросы.
cursor = conn.cursor()

# Создаём таблицу пользователей, если её ещё нет.
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        name TEXT,
        category1 TEXT,
        category2 TEXT,
        category3 TEXT,
        expenses1 REAL,
        expenses2 REAL,
        expenses3 REAL
    )
    """
)

# Сохраняем создание таблицы в базе данных.
conn.commit()


# Создаём список готовых советов по экономии.
tips = [
    "💡 Ведите бюджет и записывайте даже небольшие траты.",
    "💡 Сначала откладывайте часть дохода, а уже потом планируйте покупки.",
    "💡 Сравнивайте цены заранее и избегайте импульсивных покупок.",
    "💡 Делите расходы на обязательные и необязательные, чтобы лучше видеть лишние траты.",
    "💡 Устанавливайте лимит на развлечения и онлайн-покупки на месяц вперёд.",
]


# Создаём класс состояний для пошагового ввода трёх категорий и трёх сумм.
class FinancesForm(StatesGroup):
    # Создаём состояние для первой категории.
    category1 = State()

    # Создаём состояние для первой суммы.
    expenses1 = State()

    # Создаём состояние для второй категории.
    category2 = State()

    # Создаём состояние для второй суммы.
    expenses2 = State()

    # Создаём состояние для третьей категории.
    category3 = State()

    # Создаём состояние для третьей суммы.
    expenses3 = State()


# Создаём функцию, которая будет безопасно превращать введённый текст в денежную сумму.
def parse_amount(raw_value: str) -> float:
    # Убираем пробелы из строки и заменяем запятые на точки.
    normalized_value = raw_value.replace(" ", "").replace(",", ".")

    # Пробуем преобразовать строку в число.
    amount = float(normalized_value)

    # Проверяем, не ввёл ли пользователь отрицательное значение.
    if amount < 0:
        # Если ввёл отрицательное значение, вызываем ошибку.
        raise ValueError("Сумма не может быть отрицательной.")

    # Возвращаем число, округлённое до двух знаков после запятой.
    return round(amount, 2)


# Создаём функцию для проверки категории расходов.
def parse_category(raw_value: str) -> str:
    # Убираем лишние пробелы по краям.
    cleaned_value = raw_value.strip()

    # Проверяем, что после очистки строка не пустая.
    if not cleaned_value:
        # Если строка пустая, вызываем ошибку.
        raise ValueError("Категория не может быть пустой.")

    # Проверяем, что категория не слишком длинная.
    if len(cleaned_value) > 40:
        # Если слишком длинная, вызываем ошибку.
        raise ValueError("Категория слишком длинная.")

    # Возвращаем готовое название категории.
    return cleaned_value


# Создаём асинхронную функцию, которая запрашивает курс валют через API.
async def get_exchange_rates() -> tuple[float, float, str]:
    # Формируем адрес запроса к сервису ExchangeRate-API.
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/USD"

    # Ограничиваем общее время ожидания ответа десятью секундами.
    timeout = aiohttp.ClientTimeout(total=10)

    # Открываем асинхронную сессию HTTP-клиента.
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Выполняем GET-запрос к сервису курсов валют.
        async with session.get(url) as response:
            # Читаем ответ сервера в формате JSON.
            data = await response.json()

            # Проверяем, что HTTP-статус ответа успешный.
            if response.status != 200:
                # Если статус неуспешный, поднимаем понятную ошибку.
                raise ValueError(data.get("error-type", "Сервис валют недоступен."))

            # Проверяем логический статус ответа API.
            if data.get("result") != "success":
                # Если сервис вернул логическую ошибку, поднимаем её.
                raise ValueError(data.get("error-type", "Не удалось получить курс валют."))

            # Получаем курс доллара к рублю.
            usd_to_rub = float(data["conversion_rates"]["RUB"])

            # Получаем курс доллара к евро.
            usd_to_eur = float(data["conversion_rates"]["EUR"])

            # Проверяем, что курс доллара к евро не равен нулю.
            if usd_to_eur == 0:
                # Если ноль, не даём делить на ноль.
                raise ValueError("Получены некорректные данные по EUR.")

            # Правильно считаем курс евро к рублю через деление.
            eur_to_rub = usd_to_rub / usd_to_eur

            # Получаем строку с датой и временем обновления.
            last_update = data.get("time_last_update_utc", "время обновления не указано")

            # Возвращаем готовые курсы и строку времени обновления.
            return round(usd_to_rub, 2), round(eur_to_rub, 2), last_update


# Создаём функцию, которая вернёт главное приветственное сообщение.
def build_main_text() -> str:
    # Возвращаем красиво оформленный текст с эмодзи и заголовком.
    return (
        "💼 <b>Финансовый бот-помощник</b>\n\n"
        "Добро пожаловать!\n"
        "Я помогу вам:\n"
        "• зарегистрироваться в боте;\n"
        "• посмотреть курс валют;\n"
        "• получить совет по экономии;\n"
        "• сохранить 3 категории личных расходов.\n\n"
        "Выберите нужную кнопку в меню ниже 👇"
    )


# Создаём функцию, которая вернёт текст справки.
def build_help_text() -> str:
    # Возвращаем понятную памятку по всем возможностям бота.
    return (
        "🆘 <b>Справка по боту</b>\n\n"
        "1. Нажмите <b>📝 Регистрация в телеграм боте</b>.\n"
        "2. Нажмите <b>💱 Курс валют</b>, чтобы получить курсы USD и EUR.\n"
        "3. Нажмите <b>💡 Советы по экономии</b>, чтобы получить случайный совет.\n"
        "4. Нажмите <b>📊 Личные финансы</b>, чтобы ввести 3 категории расходов.\n\n"
        "Дополнительные команды:\n"
        "• <code>/start</code> — запустить бота;\n"
        "• <code>/menu</code> — снова показать меню;\n"
        "• <code>/help</code> — показать помощь;\n"
        "• <code>/cancel</code> — отменить текущий ввод."
    )


# Создаём функцию, которая устанавливает команды в системное меню Telegram.
async def set_main_commands() -> None:
    # Передаём список команд, которые будут видны пользователю в Telegram.
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="menu", description="Показать меню"),
            BotCommand(command="help", description="Помощь"),
            BotCommand(command="cancel", description="Отменить текущий ввод"),
        ]
    )


# Обрабатываем команду /start.
@dp.message(Command("start"))
# Обрабатываем команду /menu тем же способом.
@dp.message(Command("menu"))
async def send_start(message: Message) -> None:
    # Отправляем приветственный текст и главное меню.
    await message.answer(build_main_text(), reply_markup=keyboard)


# Обрабатываем команду /help.
@dp.message(Command("help"))
async def send_help(message: Message) -> None:
    # Отправляем справку и оставляем клавиатуру на экране.
    await message.answer(build_help_text(), reply_markup=keyboard)


# Обрабатываем команду /cancel.
@dp.message(Command("cancel"))
async def cancel_action(message: Message, state: FSMContext) -> None:
    # Получаем текущее состояние пользователя.
    current_state = await state.get_state()

    # Проверяем, есть ли сейчас активный пошаговый ввод.
    if current_state is None:
        # Если активного ввода нет, сообщаем об этом пользователю.
        await message.answer("❌ Сейчас нет активного ввода.", reply_markup=keyboard)

        # Завершаем функцию.
        return

    # Очищаем текущее состояние пользователя.
    await state.clear()

    # Сообщаем, что ввод был успешно отменён.
    await message.answer("❌ Текущее действие отменено.\n\nМожете выбрать другой раздел.", reply_markup=keyboard)


# Обрабатываем нажатие кнопки регистрации.
@dp.message(F.text.in_(REGISTER_TEXTS))
async def registration(message: Message) -> None:
    # Получаем Telegram ID пользователя.
    telegram_id = message.from_user.id

    # Получаем полное имя пользователя из Telegram.
    full_name = message.from_user.full_name

    # Выполняем поиск пользователя по telegram_id в базе данных.
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))

    # Получаем одну найденную запись.
    user = cursor.fetchone()

    # Проверяем, найден ли уже такой пользователь.
    if user:
        # Если пользователь уже есть, сообщаем об этом.
        await message.answer(
            f"✅ Вы уже зарегистрированы, <b>{html.escape(full_name)}</b>!",
            reply_markup=keyboard,
        )

        # Завершаем функцию.
        return

    # Если пользователя ещё нет, добавляем его в базу данных.
    cursor.execute(
        "INSERT INTO users (telegram_id, name) VALUES (?, ?)",
        (telegram_id, full_name),
    )

    # Сохраняем изменения в базе данных.
    conn.commit()

    # Отправляем сообщение об успешной регистрации.
    await message.answer(
        f"🎉 Регистрация прошла успешно, <b>{html.escape(full_name)}</b>!\n\n"
        "Теперь можете пользоваться всеми функциями бота.",
        reply_markup=keyboard,
    )


# Обрабатываем нажатие кнопки курса валют.
@dp.message(F.text.in_(RATES_TEXTS))
async def exchange_rates(message: Message) -> None:
    # Пытаемся получить курс валют.
    try:
        # Вызываем функцию запроса курсов.
        usd_to_rub, eur_to_rub, last_update = await get_exchange_rates()

        # Отправляем красивую карточку с курсами.
        await message.answer(
            "💱 <b>Курс валют</b>\n\n"
            f"🇺🇸 <b>1 USD</b> = <b>{usd_to_rub}</b> RUB\n"
            f"🇪🇺 <b>1 EUR</b> = <b>{eur_to_rub}</b> RUB\n\n"
            f"🕒 <i>Обновлено:</i> {html.escape(last_update)}",
            reply_markup=keyboard,
        )

    # Если при запросе произошла ошибка, обрабатываем её.
    except Exception as error:
        # Отправляем пользователю понятное сообщение об ошибке.
        await message.answer(
            "⚠️ Не удалось получить данные о курсе валют.\n\n"
            f"Причина: <code>{html.escape(str(error))}</code>",
            reply_markup=keyboard,
        )


# Обрабатываем нажатие кнопки советов по экономии.
@dp.message(F.text.in_(TIPS_TEXTS))
async def send_tips(message: Message) -> None:
    # Выбираем один случайный совет из списка.
    tip = random.choice(tips)

    # Отправляем пользователю совет с красивым оформлением.
    await message.answer(
        f"💡 <b>Совет по экономии</b>\n\n{tip}",
        reply_markup=keyboard,
    )


# Обрабатываем нажатие кнопки личных финансов.
@dp.message(F.text.in_(FINANCES_TEXTS))
async def finances_start(message: Message, state: FSMContext) -> None:
    # Получаем Telegram ID пользователя.
    telegram_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь.
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))

    # Забираем найденную запись.
    user = cursor.fetchone()

    # Если пользователь ещё не зарегистрирован, просим сначала зарегистрироваться.
    if not user:
        # Отправляем понятное сообщение и оставляем клавиатуру.
        await message.answer(
            "⚠️ Сначала зарегистрируйтесь через кнопку <b>📝 Регистрация в телеграм боте</b>.",
            reply_markup=keyboard,
        )

        # Завершаем функцию.
        return

    # Устанавливаем первое состояние пошаговой формы.
    await state.set_state(FinancesForm.category1)

    # Просим ввести первую категорию расходов.
    await message.answer(
        "📊 <b>Личные финансы</b>\n\n"
        "Введите <b>первую категорию</b> расходов.\n"
        "Например: <i>Продукты</i>",
        reply_markup=keyboard,
    )


# Обрабатываем ввод первой категории.
@dp.message(FinancesForm.category1)
async def process_category1(message: Message, state: FSMContext) -> None:
    # Пытаемся проверить и очистить введённую категорию.
    try:
        # Получаем готовую категорию.
        category = parse_category(message.text)

    # Если категория неправильная, показываем ошибку.
    except ValueError:
        # Просим ввести нормальное название категории.
        await message.answer("Введите корректное название категории.\nНапример: <b>Продукты</b>")

        # Завершаем функцию.
        return

    # Сохраняем первую категорию во временное состояние FSM.
    await state.update_data(category1=category)

    # Переключаем состояние на ввод первой суммы.
    await state.set_state(FinancesForm.expenses1)

    # Просим ввести расходы по первой категории.
    await message.answer("Введите расходы для <b>первой категории</b>.\nНапример: <code>1500</code>")


# Обрабатываем ввод первой суммы.
@dp.message(FinancesForm.expenses1)
async def process_expenses1(message: Message, state: FSMContext) -> None:
    # Пытаемся преобразовать введённый текст в число.
    try:
        # Получаем первую сумму.
        amount = parse_amount(message.text)

    # Если сумма введена неправильно, сообщаем об этом.
    except ValueError:
        # Просим повторить ввод в корректном формате.
        await message.answer("Введите корректную сумму.\nНапример: <code>1500</code> или <code>1500.50</code>")

        # Завершаем функцию.
        return

    # Сохраняем первую сумму во временное состояние.
    await state.update_data(expenses1=amount)

    # Переключаем состояние на ввод второй категории.
    await state.set_state(FinancesForm.category2)

    # Просим пользователя ввести вторую категорию расходов.
    await message.answer("Введите <b>вторую категорию</b> расходов.\nНапример: <i>Транспорт</i>")


# Обрабатываем ввод второй категории.
@dp.message(FinancesForm.category2)
async def process_category2(message: Message, state: FSMContext) -> None:
    # Пытаемся проверить категорию.
    try:
        # Получаем очищенную вторую категорию.
        category = parse_category(message.text)

    # Если категория неправильная, показываем подсказку.
    except ValueError:
        # Просим пользователя ввести нормальное название категории.
        await message.answer("Введите корректное название категории.\nНапример: <b>Транспорт</b>")

        # Завершаем функцию.
        return

    # Сохраняем вторую категорию.
    await state.update_data(category2=category)

    # Переключаем состояние на ввод второй суммы.
    await state.set_state(FinancesForm.expenses2)

    # Просим ввести сумму второй категории.
    await message.answer("Введите расходы для <b>второй категории</b>.\nНапример: <code>800</code>")


# Обрабатываем ввод второй суммы.
@dp.message(FinancesForm.expenses2)
async def process_expenses2(message: Message, state: FSMContext) -> None:
    # Пытаемся превратить текст в число.
    try:
        # Получаем вторую сумму.
        amount = parse_amount(message.text)

    # Если сумма неправильная, показываем сообщение.
    except ValueError:
        # Просим повторно ввести сумму.
        await message.answer("Введите корректную сумму.\nНапример: <code>800</code> или <code>800.25</code>")

        # Завершаем функцию.
        return

    # Сохраняем вторую сумму в FSM.
    await state.update_data(expenses2=amount)

    # Переключаем состояние на ввод третьей категории.
    await state.set_state(FinancesForm.category3)

    # Просим пользователя ввести третью категорию расходов.
    await message.answer("Введите <b>третью категорию</b> расходов.\nНапример: <i>Развлечения</i>")


# Обрабатываем ввод третьей категории.
@dp.message(FinancesForm.category3)
async def process_category3(message: Message, state: FSMContext) -> None:
    # Пытаемся проверить третью категорию.
    try:
        # Получаем очищенную третью категорию.
        category = parse_category(message.text)

    # Если категория введена неправильно, просим повторить.
    except ValueError:
        # Отправляем понятную подсказку.
        await message.answer("Введите корректное название категории.\nНапример: <b>Развлечения</b>")

        # Завершаем функцию.
        return

    # Сохраняем третью категорию в FSM.
    await state.update_data(category3=category)

    # Переключаем состояние на ввод третьей суммы.
    await state.set_state(FinancesForm.expenses3)

    # Просим ввести расходы по третьей категории.
    await message.answer("Введите расходы для <b>третьей категории</b>.\nНапример: <code>1200</code>")


# Обрабатываем ввод третьей суммы и завершаем форму.
@dp.message(FinancesForm.expenses3)
async def process_expenses3(message: Message, state: FSMContext) -> None:
    # Пытаемся преобразовать введённый текст в число.
    try:
        # Получаем третью сумму.
        amount = parse_amount(message.text)

    # Если сумма введена с ошибкой, просим повторить.
    except ValueError:
        # Отправляем сообщение с примером правильного формата.
        await message.answer("Введите корректную сумму.\nНапример: <code>1200</code> или <code>1200.75</code>")

        # Завершаем функцию.
        return

    # Сохраняем третью сумму в FSM.
    await state.update_data(expenses3=amount)

    # Получаем все собранные данные из FSM.
    data = await state.get_data()

    # Получаем Telegram ID текущего пользователя.
    telegram_id = message.from_user.id

    # Обновляем запись пользователя в базе данных.
    cursor.execute(
        """
        UPDATE users
        SET category1 = ?, expenses1 = ?, category2 = ?, expenses2 = ?, category3 = ?, expenses3 = ?
        WHERE telegram_id = ?
        """,
        (
            data["category1"],
            data["expenses1"],
            data["category2"],
            data["expenses2"],
            data["category3"],
            data["expenses3"],
            telegram_id,
        ),
    )

    # Сохраняем изменения в базе данных.
    conn.commit()

    # Считаем общую сумму расходов по трём категориям.
    total = data["expenses1"] + data["expenses2"] + data["expenses3"]

    # Очищаем состояние пользователя, потому что ввод завершён.
    await state.clear()

    # Экранируем категории, чтобы безопасно показать их в HTML.
    category1_safe = html.escape(data["category1"])
    category2_safe = html.escape(data["category2"])
    category3_safe = html.escape(data["category3"])

    # Отправляем красивую итоговую сводку пользователю.
    await message.answer(
        "✅ <b>Категории и расходы сохранены!</b>\n\n"
        f"1️⃣ {category1_safe} — <b>{data['expenses1']}</b>\n"
        f"2️⃣ {category2_safe} — <b>{data['expenses2']}</b>\n"
        f"3️⃣ {category3_safe} — <b>{data['expenses3']}</b>\n\n"
        f"💰 <b>Итого:</b> {total:.2f}",
        reply_markup=keyboard,
    )


# Создаём главную асинхронную функцию запуска бота.
async def main() -> None:
    # Устанавливаем команды в системное меню Telegram.
    await set_main_commands()

    # Удаляем старый webhook и сбрасываем накопившиеся обновления.
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем polling и разрешаем только те типы обновлений, которые реально используются.
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


# Проверяем, что файл app.py запущен напрямую.
if __name__ == "__main__":
    # Запускаем бота внутри блока try, чтобы аккуратно завершать работу.
    try:
        # Запускаем главную функцию через asyncio.
        asyncio.run(main())

    # Перехватываем стандартное завершение с клавиатуры.
    except (KeyboardInterrupt, SystemExit):
        # Печатаем понятное сообщение в консоль.
        print("Бот остановлен пользователем.")

    # Выполняем завершающие действия в любом случае.
    finally:
        # Закрываем соединение с базой данных.
        conn.close()