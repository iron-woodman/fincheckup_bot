import pandas as pd
import os

class Shablon:
    def __init__(self):
        self.data = []  # шаблоны ответов пользователю исходя из набранных баллов
        self.df = None  # DataFrame для данных из Excel
        self.excel_file = r'..\..\quiz_data\quiz_shablon.xlsx'
        # Проверка существования файла
        if not os.path.exists(self.excel_file):
            raise FileNotFoundError(f"Файл не найден: {self.excel_file}")
        self.process_shablon_file(self.excel_file)
        self.extract_shablon_data()


    def process_shablon_file(self, excel_file):
        """Загрузка данных из Excel файла."""
        self.df = pd.read_excel(excel_file, header=0)
        self.df.columns = self.df.columns.str.strip()
        self.df['Баллы'] = self.df['Баллы'].str.strip()
        self.df['Результат'] = self.df['Результат'].str.strip()



    def extract_shablon_data(self):
        """Извлекает шаблоны ответов из DataFrame."""
        self.data.clear()
        for index, row in self.df.iterrows():
            score_interval = str(row['Баллы'])
            result_description = str(row['Результат'])
            # Удаление пробелов и преобразование строки в две переменные
            start, end = map(int, score_interval.replace(' ', '').split('-'))
            self.data.append({'score_start': start, 'score_end': end, 'description': result_description})



    def get_shablon(self, score: int):
        """Определяем нужный вариант (шаблон) ответа исходя из набранных баллов"""
        for res in self.data:
            if res['score_start'] < score < res['score_end']:
                return res['description']

        return None

def main():
    shablon = Shablon()
    shablon.extract_shablon_data()
    print(shablon.get_shablon(-554))




if __name__ == "__main__":
    main()
