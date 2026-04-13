import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

user_mode = {}

if not os.getenv("GROQ_API_KEY"):
    print("❌ GROQ_API_KEY не найден")

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💡 Идеи"), KeyboardButton(text="📝 Сценарий")],
        [KeyboardButton(text="💰 Монетизация"), KeyboardButton(text="📊 Анализ")]
    ],
    resize_keyboard=True
)


async def ask_gpt(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Ты - энергичный и креативный AI-помощник для креаторов и бизнесменов. Отвечай живо, c эмодзи 🔥⚡🚀, короткими абзацами, без скучной теории, как будто объясняешь другу c учетом аудитории в Таджикистане и СНГ. Вот формат ответа 🔥 Идея, ⚡ Почему это работает, 🚀 Как сделать, 💰 Как заработать (если можно). Отвечай БЕЗ Markdown (** не используй) в место него используй HTML: <b>жирный</b> и <i>курсив</i>"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        print("❌ Ошибка:", e)
        return "⚠️ Ошибка API. Попробуй позже."

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🚀 NeuroForge AI\n\nВыбери, что хочешь сделать:",
        reply_markup=keyboard
    )

@dp.message(lambda message: message.text == "💡 Идеи")
async def ideas_mode(message: types.Message):
    user_mode[message.from_user.id] = "ideas"
    await message.answer("Напиши тему, и я придумаю идеи 🔥")


@dp.message(lambda message: message.text == "📝 Сценарий")
async def script_mode(message: types.Message):
    user_mode[message.from_user.id] = "script"
    await message.answer("Напиши тему, и я создам сценарий 🎬")


@dp.message(lambda message: message.text == "💰 Монетизация")
async def money_mode(message: types.Message):
    user_mode[message.from_user.id] = "money"
    await message.answer("Напиши нишу, и я предложу способы заработка 💸")


@dp.message(lambda message: message.text == "📊 Анализ")
async def analyze_mode(message: types.Message):
    user_mode[message.from_user.id] = "analyze"
    await message.answer("Отправь идею, и я её улучшу 📈")

@dp.message()
async def handle(message: types.Message):
    mode = user_mode.get(message.from_user.id)

    if not mode:
        await message.answer("Сначала выбери режим 👇", reply_markup=keyboard)
        return

    if mode == "ideas":
        prompt = f"Дай 5 вирусных идей для контента на тему: {message.text} (с учетом аудитории в Таджикистане)"

    elif mode == "script":
        prompt = f"Напиши короткий сценарий для TikTok/Shorts на тему: {message.text}"

    elif mode == "money":
        prompt = f"Как заработать на этом в Таджикистане: {message.text}"

    elif mode == "analyze":
        prompt = f"""
        Проанализируй идею: {message.text}

        Дай:
        1. Оценку от 1 до 10
        2. Почему
        3. Как улучшить
        Коротко и по делу
        """

    await bot.send_chat_action(message.chat.id, "typing")
    answer = await ask_gpt(prompt)
    formatted = f"""
    ✨ NeuroForge AI

    {answer}

    🔥 Создавай. Улучшай. Зарабатывай.
    """
    await message.answer(formatted, parse_mode="HTML")
    await message.answer("⚡Хочешь глубже? Выбери другую функцию 👇")
    return

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))