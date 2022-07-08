from aiogram.dispatcher.filters.state import State, StatesGroup


class GameStage(StatesGroup):
    waiting_enter_opponent_id = State()
    waiting_opponent = State()
    give_dice = State()
    get_dice_stage = State()
    turn_check_stage = State()
    game_stage = State()
    end_round = State()
