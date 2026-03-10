import requests
import time, random
from enum import Enum
from dotenv import load_dotenv
import os

load_dotenv()

class GameState(Enum):
    START_COMMAND = 1
    STATE_ADD_TASK = 2

class Bot:
    TOKEN = os.getenv('BOT_TOKEN')

    def __init__(self):
        self.api_url = 'https://api.telegram.org/bot'
        self.url_cats = 'https://api.thecatapi.com/v1/images/search'
        self.offset = -1
        self.timeout = 10
        self.state = GameState.START_COMMAND
        self.tasks = []

    def get_updates(self):
        url = f'{self.api_url}{self.TOKEN}/getUpdates?offset={self.offset}&timeout={self.timeout}'
        response = requests.get(url)
        return response.json()

    def send_message(self, chat_id, text):
        url = f'{self.api_url}{self.TOKEN}/sendMessage?chat_id={chat_id}&text={text}'
        requests.get(url)

    def randomCat(self, chat_id):
        cat_resp = requests.get(self.url_cats)
        if (cat_resp.status_code == 200):
            cat_link = cat_resp.json()[0]['url']
            print(cat_link)
            url_cat = f'{self.api_url}{self.TOKEN}/sendPhoto?chat_id={chat_id}&photo={cat_link}'
            requests.get(url_cat)
        
    def printTasks(self, chat_id):
        str_tsks = ', '.join(self.tasks)
        self.send_message(chat_id, str_tsks)

    def _handleComand(self, chat_id, command: str):
        if command == "/add":
            self.send_message(chat_id, 'Добавь задачу по приколу')
            self.state = GameState.STATE_ADD_TASK
        elif command == "/tasks":
            self.printTasks(chat_id)
        elif command.lower() == "хочу котика":
            self.randomCat(chat_id)
        else:
            self.send_message(chat_id, "Ты гей? Нет такой команды")


    def handle_state(self):
        updates = self.get_updates()
        if updates.get('result'):
            for update in updates['result']:
                self.offset = update['update_id'] + 1
                if 'message' not in update or 'text' not in update['message']:
                    continue
                chat_id = update['message']['chat']['id']
                text = update['message']['text']
            if self.state == GameState.START_COMMAND:
                self._handleComand(chat_id, text)              
            elif self.state == GameState.STATE_ADD_TASK:
                self.tasks.append(text)
                self.state = GameState.START_COMMAND
            print(self.tasks)

    def run(self):
        while True:
            self.handle_state()
            time.sleep(0.1)

if __name__ == '__main__':
    bot = Bot()
    bot.run()




