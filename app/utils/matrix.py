## -*- coding: utf-8 -*-

import pandas as pd
import os
import asyncio
import aiofiles
from io import StringIO

class Matrix:
    def __init__(self, excel_file):
        self.questions = []  # Список вопросов
        self.df = None  # DataFrame для данных из Excel
        self.excel_file = excel_file
        # Проверка существования файла
        if not os.path.exists(self.excel_file):
            raise FileNotFoundError(f"Файл не найден: {self.excel_file}")
        #self.process_matrix_file(self.excel_file)
        #self.extract_questions()

    async def process_matrix_file(self, excel_file):
        """Асинхронная загрузка данных из Excel файла."""
        #df = await asyncio.to_thread(pd.read_excel, excel_file, header=1)
        try:
            df = await asyncio.to_thread(pd.read_excel, excel_file, header=1)
            df.columns = df.columns.str.strip()
            df['Ответы / критерии (вес) / баллы'] = df['Ответы / критерии (вес) / баллы'].str.strip()
            self.df = df
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            self.df = pd.DataFrame()  #  пустой DataFrame, чтобы избежать ошибок

    async def extract_questions(self):
        """Извлекает вопросы и варианты ответов с баллами из DataFrame."""
        questions = []
        question = ''
        options = []
        question_type=''
        for index, row in self.df.iterrows():
            text = str(row['Ответы / критерии (вес) / баллы'])
            if text == 'nan':
                continue
            if '?' in text:
                if question != '':
                    questions.append({'question': question, 'question_type': question_type, 'options': options})
                question = text
                options = []
                if 'несколько вариантов ответа' in question:
                    question_type = "multiple_choice"
                else:
                    question_type = "single_choice"
                continue
            else:
                options.append(text)

        if question != '':
            questions.append({'question': question, 'question_type': question_type,'options': options})

        self.questions = questions

    async def calculate_points(self, selected_answers):
        """Вычисляет общее количество баллов на основе выбранных ответов."""
        total_points = 0

        for answer in selected_answers:
            print(f"Обрабатываем ответ: {answer}")
            answer = answer.strip()
            matching_rows = self.df[self.df['Ответы / критерии (вес) / баллы'] == answer]

            base_score = matching_rows['Базовые баллы'].values
            if len(base_score) > 0:
                total_points += base_score[0]
                print(f"{answer}: Базовый балл = {base_score[0]}")
            else:
                print(f"{answer}: Базовый балл не найден")
                continue

            correction_sum = 0
            for col in self.df.columns[3:]:
                if col not in selected_answers or col == answer:
                    continue
                correction = matching_rows[col].values
                if pd.notna(correction[0]):
                    correction_sum += correction[0]

            total_points += correction_sum

        return total_points

async def main():
    matrix = Matrix(r'..\..\quiz_data\quiz_matrix.xlsx')
    await matrix.process_matrix_file(matrix.excel_file)  # Загрузка файла
    await matrix.extract_questions()  # Извлечение вопросов
    selected_answers = ["Покупка жилья", "От 35 до 45 лет", "2 ребенка"]
    total_score = matrix.calculate_points(selected_answers)
    print("Общее количество баллов:", total_score)

    for q in matrix.questions:
        print(q, '\n')

if __name__ == "__main__":
    asyncio.run(main())
