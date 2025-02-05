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


selected_answers = ["Покупка жилья", "От 35 до 45 лет", "2 ребенка"]



def extract_questions_from_excel(file_path):
    # Загружаем данные из Excel файла
    df = pd.read_excel(file_path, header=1)  # Указание, что заголовки начинаются со второй строки (если необходимо)

    # Удаляем пробелы в названиях столбцов
    df.columns = df.columns.str.strip()

    questions = []
    question = ''
    options = []
    # Обходим строки DataFrame
    for index, row in df.iterrows():
        text = str(row['Ответы / критерии (вес) / баллы'])  # Предполагаем, что это текст вопроса
        if text == 'nan' :
            continue
        if '?' in text:
            if question != '':
                questions.append({'Вопрос': question, 'Варианты': options})
            question = text
            options = []
            continue
        else:
            options.append({'option': text, 'score': row['Базовые баллы']})

    if question != '':
        questions.append({'Вопрос': question, 'Варианты': options})

    return questions




def main():
    # Рассчитываем общее количество баллов
    total_score = calculate_points(selected_answers)
    print("Общее количество баллов:", total_score)

    # Пример вызова функции
    questions_list = extract_questions_from_excel('V 1.5 Баллы и коэф Сценарий бота .xlsx')
    for q in questions_list:
        print(q, '\n')


if __name__ == "__main__":
    main()
