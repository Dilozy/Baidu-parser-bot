from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from baidu_parser import run_parser
from database.db import find_data_in_db, add_new_example
import bot_tools.keyboards as kb


router = Router()


class CheckText(StatesGroup):
    parser_input_phrase = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("<b>Привет!, я бот, который умеет проверять использование сочетаний на китайском языке</b>\n\n" 
                         "Взаимодействие с ботом осуществляется с помощью следующих команд:\n\n"
                         "/start - начало работы бота\n"
                         "/report - сообщить об ошибке в работе бота\n"
                         "/parse - поиск совпадений в Baidu по введенном сочетанию\n",
                         parse_mode=ParseMode.HTML)


@router.message(Command("report"))
async def cmd_rep(message: Message):
    await message.answer("Ошибки в работе бота могут возникать в следующих случаях:\n\n"
                         "1. У вас включен VPN (это может привести к некорректной работе бота)"
                         "2. Baidu не отвечает\n"
                         "В случае возникновения других ошибок, сообщите, пожалуйста, об этом")


@router.message(Command("parse"))
async def get_phrase(message: Message, state: FSMContext):
    await state.set_state(CheckText.parser_input_phrase)
    await message.answer("Пожалуйста, введите сочетание для проверки")


@router.callback_query(F.data == "new_parse")
async def new_parse_query(callback: CallbackQuery, state: FSMContext):
    await get_phrase(callback.message, state)

@router.callback_query(F.data == "stop_working")
async def end_of_session(callback: CallbackQuery):
    await callback.message.answer("Еще увидимся!")


async def handle_parsed_results(message: Message, results):
    await message.answer("Найдены следующие совпадения:")
    for item in results:
        formatted_result = f"1. {item[1][0]}\n\n2. {item[1][1]}\n\nURL: {item[0]}"
        await message.answer(formatted_result, parse_mode=ParseMode.HTML)


async def handle_db_results(message: Message, results):
    await message.answer("Найдены следующие совпадения:")
    for result in results:
        answer_ = f"1. {result[1]}\n\n2. {result[2]}\n\nURL: {result[0]}"
        await message.answer(answer_, parse_mode=ParseMode.HTML)


@router.message(CheckText.parser_input_phrase)
async def get_parsing_results(message: Message, state: FSMContext):
    check_db = await find_data_in_db(message.text)

    if check_db:
        await handle_db_results(message, check_db)
    else:
        await state.update_data(parser_input_phrase=message.text)
        await message.answer("Выполняется проверка сочетания, ожидайте...")
        
        try:
            parsed_data = run_parser(message.text.strip())

            if not parsed_data:
                await message.answer("Совпадений не найдено")
            else:
                await add_new_example(message.text, parsed_data)
                await handle_parsed_results(message, parsed_data)
        
        except TimeoutException:
            await message.answer("Превышено время ожидания, попробуйте повторить запрос позже")
        
        except NoSuchElementException:
            await message.answer("Вероятно, структура сайта изменилась, сообщите об этом в поддержку")
        
        finally:
            await state.clear()

    await message.answer("Хотите проверить еще одно сочетание?", reply_markup=kb.inline_after_parse)
        

@router.message()
async def handle_unknown_command(message: Message):
    await message.answer("Бот не смог обработать эту команду\n\n"
    "Взаимодействие с ботом осуществляется с помощью следующих команд:\n\n"
                         "/start - начало работы бота\n"
                         "/report - сообщить об ошибке в работе бота\n"
                         "/parse - поиск совпадений в Baidu по введенном сочетанию\n",
                         parse_mode=ParseMode.HTML)

