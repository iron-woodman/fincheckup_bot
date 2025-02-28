## -*- coding: utf-8 -*-

import pandas as pd
import os
import asyncio

class Shablon:
    def __init__(self, excel_file):
        self.data = []  # шаблоны ответов пользователю исходя из набранных баллов
        self.df = None  # DataFrame для данных из Excel
        self.excel_file = excel_file
        # Проверка существования файла
        if not os.path.exists(self.excel_file):
            raise FileNotFoundError(f"Файл не найден: {self.excel_file}")


    async def process_shablon_file(self):
        """Загрузка данных из Excel файла."""
        self.df = pd.read_excel(self.excel_file, header=0)
        self.df.columns = self.df.columns.str.strip()
        self.df['Баллы'] = self.df['Баллы'].str.strip()
        self.df['Результат'] = self.df['Результат'].str.strip()



    async def extract_shablon_data(self):
        """Извлекает шаблоны ответов из DataFrame."""
        self.data.clear()
        if self.df is None:
            return
        for index, row in self.df.iterrows():
            score_interval = str(row['Баллы'])
            result_description = str(row['Результат'])
            # Удаление пробелов и преобразование строки в две переменные
            start, end = map(int, score_interval.replace(' ', '').split('-'))
            self.data.append({'score_start': start, 'score_end': end, 'description': result_description})



    async def get_shablon(self, score: int):
        """Определяем нужный вариант (шаблон) ответа исходя из набранных баллов"""
        for res in self.data:
            if res['score_start'] < score < res['score_end']:
                return res['description']

        return None

async def main():
    shablon = Shablon(r'..\..\quiz_data\quiz_shablon.xlsx')
    await shablon.process_shablon_file()
    await shablon.extract_shablon_data()
    data = await shablon.get_shablon(154)
    print(data)




if __name__ == "__main__":
    asyncio.run(main())
