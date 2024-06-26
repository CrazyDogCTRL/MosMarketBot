import random


def monty_hall_simulation(num_tests):
    cars = 0
    goats = 0

    for _ in range(num_tests):
        # Имитируем 3 двери: одна с машиной, две с козами
        doors = ['goat', 'goat', 'car']

        # Игрок выбирает одну из дверей случайным образом
        random.shuffle(doors)
        # Индекс выбранной двери
        choice_index = random.randrange(3)

        # Монти открывает одну из дверей с козой (не выбранную игроком)
        for i in range(3):
            if i != choice_index and doors[i] == 'goat':
                opened_index = i
                break

        # Игрок меняет свой выбор на оставшуюся закрытую дверь
        for i in range(3):
            if i != choice_index and i != opened_index:
                final_choice_index = i
                break

        # Подсчет результатов
        if doors[final_choice_index] == 'car':
            cars += 1
        else:
            goats += 1

    return cars, goats


# Запуск симуляции с 10000 тестами
num_tests = 10000
cars, goats = monty_hall_simulation(num_tests)

# Вывод результатов
print(f'Получено машин: {cars}')
print(f'Получено коз: {goats}')
