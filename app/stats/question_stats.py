from aiogram.fsm.state import State, StatesGroup
# FSM States for conversation flow
class QuestionStates(StatesGroup):

    waiting_for_question = State()
    waiting_for_creating_record_request = State()
    finish = State()