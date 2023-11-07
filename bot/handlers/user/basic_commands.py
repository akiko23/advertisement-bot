import logging

from aiogram import Bot, Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.db.repository import Repository
import bot.markups.markups as mp

router = Router()


@router.message(Command(commands=['start']), F.from_user.username)
async def command_start(
    msg: types.Message,
    state: FSMContext,
    bot: Bot,
    db: Repository
):
    user_id = msg.from_user.id
    await state.clear()

    if not await db.user_exists(user_id):
        logging.info("Here is the new user: " + str(user_id))
        await bot.send_message(user_id,
                               'Добро пожаловать в бота по выставке обьявлений! Для справки можете зайти в /help',
                               reply_markup=mp.main_menu)
        return await db.add_user(user_id, msg.from_user.username)
    await msg.answer('Добро пожаловать снова!', reply_markup=mp.main_menu)


@router.message(Command(commands=['help']))
async def command_help(msg: types.Message):
    await msg.answer('Приветствую! Это бот для выставки объявлений. Воспользуйтесь кнопками в меню для работы '
                     'с ботом\nЕсли '
                     'вы нашли какой-то баг, или есть какие-то вопросы на счет бота, пишите разработчику '
                     '@debriy2')


@router.message(Command(commands=['creator']))
async def command_creator(msg: types.Message):
    await msg.answer(msg.from_user.id, 'Cоздатель @akiko233')


@router.message(Command(commands=['start']))
async def command_start_on_empty_username(msg: types.Message):
    await msg.answer("Для начала работы с ботом установите username в настройках телеграма")
