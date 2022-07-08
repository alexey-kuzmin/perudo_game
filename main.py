from os import getenv
from sys import exit
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dashes_class import *
from db import BotDB
from play_stages import *
from random2 import choice


def on_startup():
    print('Вышел в онлайн!')


# Подключение к БД и разработанным методам
BotDB = BotDB('players_db.db')
# задаем уровень логов
logging.basicConfig(level=logging.INFO)
# инициируем бота, токен в переменной окружения
bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")
bot = Bot(token=bot_token)
# Инициируем диспетчер
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Эхо бот для теста
@dp.message_handler(commands=['start'])
async def check_in_users(message: types.Message):
    if not BotDB.user_exists(message.from_user.id):
        BotDB.add_user(message.from_user.id)
        await message.answer('Добро пожаловать! (; \nЕсли что - пиши /help')
    else:
        await message.answer('Ты вернулся! (; \nЕсли что - пиши /help')


@dp.message_handler(commands="help")
async def get_help(message: types.Message):
    await message.answer('/my_id - узнать совй id \n/new_game - для новой игры')


@dp.message_handler(commands="my_id")
async def send_id(message: types.Message):
    await message.answer(message.from_user.id)


# Добавляем возможность отмены, если пользователь передумал играть
@dp.message_handler(state=GameStage.all_states, commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state=GameStage.all_states)
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('ОК')


# ОТПРАВКА СООБЩЕНИЯ В ДРУГОЙ ЧАТ
# @dp.message_handler(commands="new_game")
# async def new_game(message: types.Message):
#     await message.bot.send_dice(-100123456789, emoji="🎲")


@dp.message_handler(commands="new_game")
async def game_start(message: types.Message):
    """Начинаем игру"""
    BotDB.flag_active_session(message.from_user.id)
    await GameStage.waiting_enter_opponent_id.set()  # На какой стадии зависаем!
    await message.answer('Введите id оппонента:')


# Сюда приходит ответ с id соперника
@dp.message_handler(state=GameStage.waiting_enter_opponent_id)
async def check_opponent_in_bd(message: types.Message):
    if not BotDB.user_exists(message.text):
        await message.reply('Такого игрока у меня нет((')
        return
    elif BotDB.check_active_session(message.text):
        await message.answer('Ваш соперник в другой партии((\nПодождите и попробуйте ещё')
        return
    else:
        # await bot.send_message(message.text, 'Кажется с вами хотят сыграть!')
        BotDB.update_opponent(message.from_user.id, message.text)
        BotDB.update_opponent(message.text, message.from_user.id)
        await bot.send_message(message.from_user.id, 'Кажется с вами хотят сыграть!')  # Для теста
        await GameStage.waiting_opponent.set()
        await bot.send_message(message.from_user.id, 'Что ответить? (Да/Нет)')  # Для теста
        # await bot.send_message(message.text, 'Что ответить? (Да/Нет)')
        state = dp.current_state(chat=message.text,
                                 user=message.text)
        await state.set_state(GameStage.waiting_opponent)


@dp.message_handler(state=GameStage.waiting_opponent)
async def confirm_start(message: types.Message, state: FSMContext):
    # Установка состояния другого пользователя
    # state = dp.current_state(chat=chat_id, user=user_id)
    # await state.set_state(User.accepted)
    # chat_id - id чата, который должен быть равен id пользователя, если это переписка с пользователем
    # User.accepted - состояние  в которое мы хотим привести пользователя
    if message.text == 'Нет':
        BotDB.update_opponent(message.from_user.id, opponent_id=None)
        await bot.send_message(BotDB.get_user_opponent(message.from_user.id), 'Кажется с вами не хотят играть((')
        await state.finish()
    elif message.text == 'Да':
        BotDB.flag_active_session(BotDB.get_user_opponent(message.from_user.id))

        user_id = message.from_user.id
        user_dice = HandDice(hand_dice=BotDB.get_user_dice(user_id))
        opponent_dice = HandDice(hand_dice=BotDB.get_user_dice(BotDB.get_user_opponent(user_id)))
        user_dice.new_dice_roll()
        opponent_dice.new_dice_roll()

        BotDB.update_dice(user_id, user_dice.get_hand_dice())
        BotDB.update_dice(BotDB.get_user_opponent(user_id), opponent_dice.get_hand_dice())
    else:
        await message.answer('Что-то пошло не так...Так Да или Нет?')
        return

    await message.answer('Кажется все готово, начинаем?')
    await state.set_state(GameStage.give_dice)


@dp.message_handler(state=GameStage.give_dice)
async def give_dice(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer('Ваши кости:')
    await message.answer(BotDB.get_user_dice(user_id))  # Отправляем кости инициатору
    # await bot.send_message(BotDB.get_user_opponent(user_id),
    #                        BotDB.get_user_dice(user_id))     # Отправляем кости оппоненту

    await message.answer('Что ж, начнём!')
    # await bot.send_message(BotDB.get_user_opponent(user_id),
    #                        BotDB.get_user_dice(user_id))

    await message.answer('Посмотрим, кто будет ходить...')
    # await bot.send_message(BotDB.get_user_opponent(user_id), 'Посмотрим, кто будет ходить...')
    # Кнопка бросить монетку
    turn = choice((True, False))
    # if turn:
    if True:
        BotDB.update_turn(user_id)
        await message.answer('Ваш ход')
        # await bot.send_message(user_id, 'Ходит оппонент')
        await GameStage.game_stage.set()
        # state = dp.current_state(chat=BotDB.get_user_opponent(message.from_user.id),
        #                          user=message.from_user.id)
        # await state.set_state(GameStage.check_turn)
    else:
        BotDB.update_turn(BotDB.get_user_opponent(user_id))
        # await bot.send_message(BotDB.get_user_opponent(user_id), 'Ваш ход')
        await message.answer('Ходит оппонент, ожидайте')
        await GameStage.turn_check_stage.set()
        # state = dp.current_state(chat=BotDB.get_user_opponent(message.from_user.id),
        #                          user=message.from_user.id)
        # await state.set_state(GameStage.game_stage)


@dp.message_handler(state=GameStage.turn_check_stage)
async def check_turn(message: types.Message, state: FSMContext):
    if BotDB.get_turn(message.from_user.id):
        await GameStage.game_stage.set()
    else:
        await message.answer('Дождитесь своего хода!')


@dp.message_handler(state=GameStage.game_stage)
async def game(message: types.Message, state: FSMContext):
    if message.text == 'не верю':
        await GameStage.end_round.set()
        # state = dp.current_state(chat=BotDB.get_user_opponent(message.from_user.id),
        #                          user=message.from_user.id)
        # await state.set_state(GameStage.end_round)
        return
    elif message.text.split()[0].isalnum() and message.text.split()[1] in [str(i) for i in range(1, 6)]:
        async with state.proxy() as data:
            data['dice'] = (int(message.text.split()[0]), message.text.split()[1])
        # await bot.send_message(BotDB.get_user_opponent(message.from_user.id), message.text)
        # await GameStage.turn_check_stage.set()
        # state = dp.current_state(chat=BotDB.get_user_opponent(message.from_user.id),
        #                          user=message.from_user.id)
        # await state.set_state(GameStage.game_stage)
    else:
        await message.answer('Напишите ход ввида "Количество Номинал", например - 2 5 - две пятерки')
        return

    # keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # for d in range(1, 11):
    #     keyboard.add(d)
    # await message.answer("Выберите общее количество костей:", reply_markup=keyboard)
    # await GameStage.game_stage.set()


@dp.message_handler(state=GameStage.end_round)
async def end_round(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer("----end_round---")
    async with state.proxy() as data:
        count, nominal = data['dice']
    all_dice = HandDice(BotDB.get_user_dice(user_id)) + HandDice(BotDB.get_user_dice(BotDB.get_user_opponent(user_id)))
    await message.answer(all_dice.get_hand_dice())
    if all_dice.get_hand_dice().count(nominal) >= count:
        user_dice = HandDice(BotDB.get_user_dice(user_id))
        user_dice.del_dice()
        user_dice.new_dice_roll()
        BotDB.update_dice(user_id, user_dice)

        opponent_id = BotDB.get_user_opponent(user_id)
        opponent_dice = HandDice(BotDB.get_user_dice(opponent_id))
        opponent_dice.new_dice_roll()
        BotDB.update_dice(opponent_id, opponent_dice)
    else:
        user_dice = HandDice(BotDB.get_user_dice(user_id))
        user_dice.new_dice_roll()
        BotDB.update_dice(user_id, user_dice)

        opponent_id = BotDB.get_user_opponent(user_id)
        opponent_dice = HandDice(BotDB.get_user_dice(opponent_id))
        opponent_dice.del_dice()
        opponent_dice.new_dice_roll()
        BotDB.update_dice(opponent_id, opponent_dice)

        if user_dice.get_number_of_dice() == 0:
            await message.answer('Вы проиграли(')
            await bot.send_message(opponent_id, 'Вы выиграли!')
        elif opponent_dice.get_number_of_dice() == 0:
            await message.answer('Вы выиграли!')
            await bot.send_message(opponent_id, 'Вы проиграли(')
        else:
            await GameStage.turn_check_stage.set()

if __name__ == '__main__':
    # user_id = 777

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup())
