from flask import Blueprint, request, jsonify
from datetime import datetime

# Создаем Blueprint
calculator_routes = Blueprint('calculator', __name__)

# Функция для расчета ежемесячных сбережений


@calculator_routes.route('/savings-goal', methods=['POST'])
def calculate_savings_goal():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'Отсутствуют данные запроса'}), 400

    # Получаем параметры из запроса
    target_amount = data.get('target_amount')
    target_date_str = data.get('target_date')
    current_savings = data.get('current_savings', '0')

    # Проверка наличия необходимых параметров
    if not target_amount or not target_date_str:
        return jsonify({'message': 'Необходимо указать целевую сумму и дату'}), 400

    try:
        # Преобразуем строковые значения в числа
        target_amount = float(target_amount)
        current_savings = float(current_savings) if current_savings else 0

        # Проверяем корректность значений
        if target_amount <= 0:
            return jsonify({'message': 'Целевая сумма должна быть положительной'}), 400

        if current_savings < 0:
            return jsonify({'message': 'Текущие сбережения не могут быть отрицательными'}), 400

        # Преобразуем строковую дату в объект datetime
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
        current_date = datetime.now()

        # Если дата в прошлом, возвращаем ошибку
        if target_date <= current_date:
            return jsonify({'message': 'Дата цели должна быть в будущем'}), 400

        # Вычисляем количество месяцев до целевой даты
        months_remaining = (target_date.year - current_date.year) * \
            12 + (target_date.month - current_date.month)

        # Вычисляем сумму, которую нужно накопить
        amount_to_save = target_amount - current_savings

        # Результат
        result = {
            'target_amount': str(target_amount),
            'current_savings': str(current_savings),
            'amount_to_save': str(max(0, amount_to_save)),
            'months_remaining': months_remaining,
        }

        # Если нужно накопить больше нуля и есть время для накопления
        if amount_to_save > 0 and months_remaining > 0:
            # Ежемесячная сумма сбережений
            required_monthly_savings = amount_to_save / months_remaining
            result['required_monthly_savings'] = str(required_monthly_savings)
        else:
            # Если накоплений достаточно или целевая сумма достигнута
            result['required_monthly_savings'] = '0'
            if amount_to_save <= 0:
                result['message'] = 'Вы уже накопили достаточную сумму для достижения цели'

        return jsonify(result)

    except ValueError:
        return jsonify({'message': 'Некорректный формат чисел или даты'}), 400
    except Exception as e:
        return jsonify({'message': f'Ошибка при расчете: {str(e)}'}), 500
