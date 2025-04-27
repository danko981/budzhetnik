from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
import os
import datetime
import uuid

# Создаем Blueprint
categories_routes = Blueprint('categories', __name__)

# Путь к файлу для хранения категорий
CATEGORIES_FILE = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'categories.json')

# Проверяем наличие директории для данных
os.makedirs(os.path.dirname(CATEGORIES_FILE), exist_ok=True)

# Функция для загрузки категорий из файла


def load_categories():
    try:
        if os.path.exists(CATEGORIES_FILE):
            with open(CATEGORIES_FILE, 'r') as file:
                return json.load(file)
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла категорий: {e}")
        return []

# Функция для сохранения категорий в файл


def save_categories(categories):
    try:
        with open(CATEGORIES_FILE, 'w') as file:
            json.dump(categories, file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении файла категорий: {e}")
        return False

# Маршрут для получения всех категорий пользователя


@categories_routes.route('', methods=['GET'])
def get_categories():
    user_id = request.args.get('user_id')

    categories = load_categories()

    # Если указан user_id, фильтруем категории по пользователю
    if user_id:
        categories = [cat for cat in categories if cat.get(
            'user_id') == user_id]

    return jsonify(categories)

# Маршрут для создания новой категории


@categories_routes.route('', methods=['POST'])
def create_category():
    try:
        data = request.get_json()

        if not data or not data.get('name') or not data.get('type') or not data.get('user_id'):
            return jsonify({'message': 'Необходимо указать название, тип и ID пользователя'}), 400

        # Загружаем существующие категории
        categories = load_categories()

        # Создаем новую категорию
        new_category = {
            'id': str(uuid.uuid4()),
            'name': data['name'],
            'type': data['type'],
            'color': data.get('color', '#CCCCCC'),
            'icon': data.get('icon', 'default'),
            'user_id': data['user_id'],
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat()
        }

        # Добавляем категорию в список
        categories.append(new_category)

        # Сохраняем обновленный список категорий
        if save_categories(categories):
            return jsonify(new_category), 201
        else:
            return jsonify({'message': 'Ошибка при сохранении категории'}), 500

    except Exception as e:
        print(f"Ошибка при создании категории: {e}")
        return jsonify({'message': 'Ошибка сервера при создании категории'}), 500

# Маршрут для получения конкретной категории


@categories_routes.route('/<category_id>', methods=['GET'])
def get_category(category_id):
    categories = load_categories()

    # Ищем категорию по ID
    category = next(
        (cat for cat in categories if cat['id'] == category_id), None)

    if not category:
        return jsonify({'message': 'Категория не найдена'}), 404

    return jsonify(category)

# Маршрут для обновления категории


@categories_routes.route('/<category_id>', methods=['PUT'])
def update_category(category_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({'message': 'Нет данных для обновления'}), 400

        categories = load_categories()

        # Находим индекс категории для обновления
        category_index = next((i for i, cat in enumerate(
            categories) if cat['id'] == category_id), None)

        if category_index is None:
            return jsonify({'message': 'Категория не найдена'}), 404

        # Обновляем данные категории
        categories[category_index].update({
            'name': data.get('name', categories[category_index]['name']),
            'type': data.get('type', categories[category_index]['type']),
            'color': data.get('color', categories[category_index]['color']),
            'icon': data.get('icon', categories[category_index]['icon']),
            'updated_at': datetime.datetime.now().isoformat()
        })

        # Сохраняем обновленный список категорий
        if save_categories(categories):
            return jsonify(categories[category_index])
        else:
            return jsonify({'message': 'Ошибка при сохранении обновленной категории'}), 500

    except Exception as e:
        print(f"Ошибка при обновлении категории: {e}")
        return jsonify({'message': 'Ошибка сервера при обновлении категории'}), 500

# Маршрут для удаления категории


@categories_routes.route('/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        categories = load_categories()

        # Находим индекс категории для удаления
        category_index = next((i for i, cat in enumerate(
            categories) if cat['id'] == category_id), None)

        if category_index is None:
            return jsonify({'message': 'Категория не найдена'}), 404

        # Удаляем категорию из списка
        deleted_category = categories.pop(category_index)

        # Сохраняем обновленный список категорий
        if save_categories(categories):
            return jsonify({'message': 'Категория успешно удалена', 'category': deleted_category})
        else:
            return jsonify({'message': 'Ошибка при удалении категории'}), 500

    except Exception as e:
        print(f"Ошибка при удалении категории: {e}")
        return jsonify({'message': 'Ошибка сервера при удалении категории'}), 500
