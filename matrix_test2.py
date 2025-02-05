import pandas as pd

# Загрузка данных из Excel файла
df = pd.read_excel('V 1.5 Баллы и коэф Сценарий бота .xlsx', header=1)

# Удаление начальных и конечных пробелов в названиях столбцов
df.columns = df.columns.str.strip()

# Удаление начальных и конечных пробелов в вариантах ответов
df['Ответы / критерии (вес) / баллы'] = df['Ответы / критерии (вес) / баллы'].str.strip()

def calculate_points(selected_answers):
    total_points = 0

    # Переберем анкетируемые ответы
    # for index, answer in selected_answers.items():
    for answer in selected_answers:

        print(f"Обрабатываем ответ: {answer}")
        # Удаляем пробелы из выбранного ответа
        answer = answer.strip()

        # Выводим строки, которые соответствуют данному ответу
        matching_rows = df[df['Ответы / критерии (вес) / баллы'] == answer]
        # print("Строки в DataFrame для этого ответа:")
        # print(matching_rows)

        # Найдем базовый балл
        base_score = matching_rows['Базовые баллы'].values
        if len(base_score) > 0:
            total_points += base_score[0]  # Добавляем базовый балл
            print(f"{answer}: Базовый балл = {base_score[0]}")
        else:
            print(f"{answer}: Базовый балл не найден")
            continue  # Переходим к следующему ответу, если базовый балл не найден

        # Соберем корректирующие баллы только из выбранных ответов
        correction_sum = 0
        for col in df.columns[3:]:  # Предполагаем, что корректирующие баллы начинаются с 3-го столбца
            # Проверяем наличие корректирующего балла
            if col not in selected_answers or col == answer:
                continue
            correction = matching_rows[col].values
            print(f'КК {col}:', correction[0])
            if pd.notna(correction[0]):
                correction_sum += correction[0]  # Добавляем корректирующий балл в сумму

        # Выводим корректирующие баллы
        if correction_sum > 0:
            print(f"{answer}: Корректирующий балл = {correction_sum}")
        else:
            print(f"{answer}: Корректирующий балл = 0")

        total_points += correction_sum  # Подсчитываем общую сумму баллов

    return total_points

# Пример выбранных ответов анкетируемого
# selected_answers = {
#     1: "Покупка жилья",                   # Ваши цели и планы на ближайшие 5 лет?
#     2: "От 35 до 45 лет",                 # Ваш возраст?
#     3: "2 ребенка"                         # Количество детей до 18 лет?
# }
selected_answers = ["Покупка жилья", "От 35 до 45 лет", "2 ребенка"]



def extract_questions_from_excel(file_path):
    # Загружаем данные из Excel файла
    df = pd.read_excel(file_path, header=1)

    # Удаляем пробелы в названиях столбцов
    df.columns = df.columns.str.strip()

    questions = []

    # Обходим строки DataFrame
    for index, row in df.iterrows():
        question_text = row['Ответы / критерии (вес) / баллы']  # Текст вопроса
        if pd.isna(question_text):  # Пропускаем строки без текста вопроса
            continue

        options = []
        # Ищем варианты ответов и их базовые баллы
        for option_index in range(3, len(row)):  # Предполагаем, что варианты начинаются с третьего индекса
            option_text = row[option_index]
            if pd.notna(option_text):  # Проверяем, что значение не NaN
                # Проверяем, что option_text является строкой перед тем, как вызвать strip
                if isinstance(option_text, str):
                    option_text = option_text.strip()
                base_score = row['Базовые баллы'] if 'Базовые баллы' in df.columns else 0  # Базовый балл
                options.append({'text': option_text, 'base_score': base_score})  # Добавляем текст и базовый балл

        question_dict = {
            'id': index + 1,  # Используем индекс строки как ID вопроса (начинается с 1)
            'text': question_text.strip(),
            'options': options
        }

        questions.append(question_dict)

    return questions


# # Пример вызова функции
# questions_list = extract_questions_from_excel('V 1.5 Баллы и коэф Сценарий бота .xlsx')
# print(questions_list)




def main():
    # Рассчитываем общее количество баллов
    total_score = calculate_points(selected_answers)
    print("Общее количество баллов:", total_score)

    # Пример вызова функции
    questions_list = extract_questions_from_excel('V 1.5 Баллы и коэф Сценарий бота .xlsx')
    print(questions_list)


if __name__ == "__main__":
    main()
