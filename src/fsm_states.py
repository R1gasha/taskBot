from aiogram.fsm.state import State, StatesGroup

class States(StatesGroup):
    task_state = State()
    magnit_state = State()
    delete_state = State()
    timer_state = State()