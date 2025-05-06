#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для инициализации базы данных упрощенного приложения Budgetnik.
В текущей версии используется файловая структура JSON для хранения пользователей.
"""

import os
import json
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Путь к файлу хранения пользователей
USERS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'users.json')


def init_data_directory():
    """Инициализирует директорию для данных"""
    data_dir = os.path.dirname(USERS_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logging.info(f"Создана директория для данных: {data_dir}")


def create_users_file():
    """Создает файл с начальными пользователями, если он не существует"""
    if not os.path.exists(USERS_FILE):
        initial_users = [
            {
                'id': 1,
                'username': 'demo',
                'password': 'demo123',
                'email': 'demo@example.com'
            },
            {
                'id': 2,
                'username': 'test',
                'password': 'test123',
                'email': 'test@example.com'
            }
        ]

        with open(USERS_FILE, 'w') as f:
            json.dump(initial_users, f, ensure_ascii=False, indent=4)

        logging.info(f"Создан файл с пользователями: {USERS_FILE}")
    else:
        logging.info(f"Файл пользователей уже существует: {USERS_FILE}")


def main():
    """Основная функция инициализации"""
    logging.info("Начало инициализации данных...")

    # Создаем директорию для данных
    init_data_directory()

    # Создаем файл пользователей
    create_users_file()

    logging.info("Инициализация данных завершена.")


if __name__ == "__main__":
    main()
