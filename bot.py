import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from database import search_supplements, search_by_ingredient, get_all_symptoms, get_symptom_card, log_search, init_db
from seed_data import seed

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()


async def on_startup():
    """Инициализация БД и данных при старте бота"""
    init_db()
    seed()
    print("✅ База данных готова")


# ─── Форматирование карточки добавки ────────────────────────────────────────

def format_card(row: tuple) -> str:
    name, category, description, ingredients, benefits, dosage, available_ru, sanctions_note = row

    cat_emoji = "🌿" if category == "bio" else "💊"

    if available_ru:
        avail = "✅ Доступно в России"
    else:
        avail = "❌ Ограниченная доступность"

    if sanctions_note:
        avail += f"\n⚠️ {sanctions_note}"

    return (
        f"{cat_emoji} *{name}*\n\n"
        f"📋 {description}\n\n"
        f"🧪 *Состав:* {ingredients}\n"
        f"💡 *Польза:* {benefits}\n"
        f"📏 *Дозировка:* {dosage}\n\n"
        f"{avail}"
    )


# ─── /start ──────────────────────────────────────────────────────────────────

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! 🌿 Я помогу разобраться с добавками и препаратами.\n\n"
        "Просто напиши название — *магний*, *омега*, *витамин d*\n\n"
        "Или выбери команду:\n"
        "💊 /symptom — подбор по симптому\n"
        "🧪 /ingredient — найти по ингредиенту\n"
        "✅ /check — проверить доступность в РФ\n"
        "❓ /help — справка",
        parse_mode="Markdown"
    )


# ─── /help ───────────────────────────────────────────────────────────────────

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "*Как пользоваться:*\n\n"
        "1️⃣ Напиши название добавки:\n"
        "   _магний_, _омега_, _биотин_\n\n"
        "2️⃣ Напиши симптом:\n"
        "   _выпадение волос_, _плохой сон_, _усталость_\n\n"
        "3️⃣ /symptom — меню симптомов с кнопками\n\n"
        "4️⃣ /ingredient — найти все добавки по составу\n"
        "   например: _цинк_, _холекальциферол_, _EPA_\n\n"
        "5️⃣ /check — проверить доступность в РФ\n\n"
        "База пополняется каждую неделю 📚",
        parse_mode="Markdown"
    )


# ─── /symptom — меню симптомов ───────────────────────────────────────────────

@dp.message(Command("symptom"))
async def cmd_symptom(message: types.Message):
    symptoms = get_all_symptoms()

    if not symptoms:
        await message.answer("Симптом-карточки ещё не добавлены.")
        return

    buttons = []
    for symptom, emoji in symptoms:
        buttons.append([
            InlineKeyboardButton(
                text=f"{emoji} {symptom}",
                callback_data=f"sym:{symptom}"
            )
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выбери что тебя беспокоит:", reply_markup=keyboard)


# ─── Обработка нажатия на симптом ────────────────────────────────────────────

@dp.callback_query(F.data.startswith("sym:"))
async def handle_symptom_callback(callback: types.CallbackQuery):
    symptom_name = callback.data[4:]  # убираем "sym:"
    card = get_symptom_card(symptom_name)

    if not card:
        await callback.message.answer("Карточка не найдена.")
        await callback.answer()
        return

    symptom, emoji, causes, advice, supplement_names = card

    text = (
        f"{emoji} *{symptom}*\n\n"
        f"📌 *Возможные причины:*\n{causes}\n\n"
        f"💡 *Советы:*\n{advice}\n\n"
        f"💊 *Полезные добавки:*\n_{supplement_names}_\n\n"
        f"🔍 Напиши название любой из них — покажу подробную карточку"
    )

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


# ─── /ingredient — поиск по составу ─────────────────────────────────────────

# Храним состояние ожидания ингредиента для каждого пользователя
waiting_for_ingredient = set()


@dp.message(Command("ingredient"))
async def cmd_ingredient(message: types.Message):
    waiting_for_ingredient.add(message.from_user.id)
    await message.answer(
        "🧪 Введи название ингредиента — покажу все добавки где он есть.\n\n"
        "Примеры: _цинк_, _магний_, _холекальциферол_, _EPA_, _биотин_",
        parse_mode="Markdown"
    )


# ─── /check — проверка доступности в РФ ──────────────────────────────────────

waiting_for_check = set()


@dp.message(Command("check"))
async def cmd_check(message: types.Message):
    waiting_for_check.add(message.from_user.id)
    await message.answer(
        "✅ Введи название бренда или добавки — проверю доступность в России.\n\n"
        "Примеры: _Now Foods_, _Solgar_, _Thorne_, _Омега-3_",
        parse_mode="Markdown"
    )


# ─── Поиск по тексту ─────────────────────────────────────────────────────────

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_search(message: types.Message):
    query = message.text.strip()
    user_id = message.from_user.id

    if len(query) < 2:
        return

    # ── Режим поиска по ингредиенту ──
    if user_id in waiting_for_ingredient:
        waiting_for_ingredient.discard(user_id)
        results = search_by_ingredient(query)

        if not results:
            await message.answer(
                f"Добавок с ингредиентом «{query}» не найдено.\n"
                f"Попробуй другое название — например _цинк_ или _магний_",
                parse_mode="Markdown"
            )
            return

        lines = [f"🧪 Добавки содержащие *{query}* ({len(results)} шт.):\n"]
        for name, category, ingredients, benefits, available_ru in results:
            emoji = "🌿" if category == "bio" else "💊"
            avail = "✅" if available_ru else "❌"
            lines.append(f"{emoji} {avail} *{name}*\n   _{ingredients}_\n")

        await message.answer("\n".join(lines), parse_mode="Markdown")
        return

    # ── Режим проверки доступности ──
    if user_id in waiting_for_check:
        waiting_for_check.discard(user_id)
        from sanctions import check_availability
        result = check_availability(query)

        if result["available"]:
            await message.answer(
                f"✅ *{query}*\n\nДоступно в России. Можно найти в аптеках и на маркетплейсах.",
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                f"❌ *{query}*\n\n⚠️ {result['note']}",
                parse_mode="Markdown"
            )
        return

    # ── Обычный поиск ──
    results = search_supplements(query)
    found = len(results) > 0
    log_search(user_id, query, found)

    if not found:
        await message.answer(
            f"По запросу «{query}» ничего не найдено 🤔\n\n"
            f"Попробуй другое слово или выбери симптом через /symptom"
        )
        return

    if len(results) > 1:
        await message.answer(f"Нашёл {len(results)} результата по «{query}»:")

    for row in results:
        await message.answer(format_card(row), parse_mode="Markdown")


# ─── Запуск ───────────────────────────────────────────────────────────────────

async def main():
    await on_startup()
    print("✅ Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())