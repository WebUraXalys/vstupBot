from aiogram.dispatcher.filters.state import State, StatesGroup


class ExamsBals(StatesGroup):
    ua = State()
    math = State()
    history = State()
    correct_ua = State()
    correct_math = State()


class SearchUniver(StatesGroup):
    name = State()


class FirstName(StatesGroup):
    first_name = State()


class SpecCodes(StatesGroup):
    codes = State()