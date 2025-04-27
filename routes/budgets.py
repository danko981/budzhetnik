from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
import os
import datetime
import uuid

# Создаем Blueprint
budgets_routes = Blueprint('budgets', __name__)

# Путь к файлу для хранения бюджетов
BUDGETS_FILE = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'budgets.json')

# Проверяем наличие директории для данных
os.makedirs(os.path.dirname(BUDGETS_FILE), exist_ok=True)

# Функция для загрузки бюджетов из файла


def load_budgets():
    try:
        if os.path.exists(BUDGETS_FILE):
            with open(BUDGETS_FILE, 'r') as file:
                return json.load(file)
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла бюджетов: {e}")
        return []

# Функция для сохранения бюджетов в файл


def save_budgets(budgets):
    try:
        with open(BUDGETS_FILE, 'w') as file:
            json.dump(budgets, file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении файла бюджетов: {e}")
        return False

# Маршрут для получения всех бюджетов пользователя


@budgets_routes.route('', methods=['GET'])
def get_budgets():
    user_id = request.args.get('user_id')

    budgets = load_budgets()

    # Если указан user_id, фильтруем бюджеты по пользователю
    if user_id:
        budgets = [budget for budget in budgets if budget.get(
            'user_id') == user_id]

    return jsonify(budgets)

# Маршрут для создания нового бюджета


@budgets_routes.route('', methods=['POST'])
def create_budget():
    try:
        data = request.get_json()

        if not data or not data.get('name') or not data.get('amount') or not data.get('user_id'):
            return jsonify({'message': 'Необходимо указать название, сумму и ID пользователя'}), 400

        # Загружаем существующие бюджеты
        budgets = load_budgets()

        # Создаем новый бюджет
        new_budget = {
            'id': str(uuid.uuid4()),
            'name': data['name'],
            'description': data.get('description', ''),
            'amount': float(data['amount']),
            'period': data.get('period', 'monthly'),
            'start_date': data.get('start_date', datetime.datetime.now().isoformat()[:10]),
            'end_date': data.get('end_date'),
            'category_id': data.get('category_id'),
            'user_id': data['user_id'],
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat()
        }

        # Добавляем бюджет в список
        budgets.append(new_budget)

        # Сохраняем обновленный список бюджетов
        if save_budgets(budgets):
            return jsonify(new_budget), 201
        else:
            return jsonify({'message': 'Ошибка при сохранении бюджета'}), 500

    except Exception as e:
        print(f"Ошибка при создании бюджета: {e}")
        return jsonify({'message': 'Ошибка сервера при создании бюджета'}), 500

# Маршрут для получения конкретного бюджета


@budgets_routes.route('/<budget_id>', methods=['GET'])
def get_budget(budget_id):
    budgets = load_budgets()

    # Ищем бюджет по ID
    budget = next(
        (budget for budget in budgets if budget['id'] == budget_id), None)

    if not budget:
        return jsonify({'message': 'Бюджет не найден'}), 404

    return jsonify(budget)

# Маршрут для обновления бюджета


@budgets_routes.route('/<budget_id>', methods=['PUT'])
def update_budget(budget_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({'message': 'Нет данных для обновления'}), 400

        budgets = load_budgets()

        # Находим индекс бюджета для обновления
        budget_index = next((i for i, budget in enumerate(
            budgets) if budget['id'] == budget_id), None)

        if budget_index is None:
            return jsonify({'message': 'Бюджет не найден'}), 404

        # Обновляем данные бюджета
        budgets[budget_index].update({
            'name': data.get('name', budgets[budget_index]['name']),
            'description': data.get('description', budgets[budget_index]['description']),
            'amount': float(data.get('amount', budgets[budget_index]['amount'])),
            'period': data.get('period', budgets[budget_index]['period']),
            'start_date': data.get('start_date', budgets[budget_index]['start_date']),
            'end_date': data.get('end_date', budgets[budget_index]['end_date']),
            'category_id': data.get('category_id', budgets[budget_index]['category_id']),
            'updated_at': datetime.datetime.now().isoformat()
        })

        # Сохраняем обновленный список бюджетов
        if save_budgets(budgets):
            return jsonify(budgets[budget_index])
        else:
            return jsonify({'message': 'Ошибка при сохранении обновленного бюджета'}), 500

    except Exception as e:
        print(f"Ошибка при обновлении бюджета: {e}")
        return jsonify({'message': 'Ошибка сервера при обновлении бюджета'}), 500

# Маршрут для удаления бюджета


@budgets_routes.route('/<budget_id>', methods=['DELETE'])
def delete_budget(budget_id):
    try:
        budgets = load_budgets()

        # Находим индекс бюджета для удаления
        budget_index = next((i for i, budget in enumerate(
            budgets) if budget['id'] == budget_id), None)

        if budget_index is None:
            return jsonify({'message': 'Бюджет не найден'}), 404

        # Удаляем бюджет из списка
        deleted_budget = budgets.pop(budget_index)

        # Сохраняем обновленный список бюджетов
        if save_budgets(budgets):
            return jsonify({'message': 'Бюджет успешно удален', 'budget': deleted_budget})
        else:
            return jsonify({'message': 'Ошибка при удалении бюджета'}), 500

    except Exception as e:
        print(f"Ошибка при удалении бюджета: {e}")
        return jsonify({'message': 'Ошибка сервера при удалении бюджета'}), 500
