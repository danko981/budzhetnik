import pytest
import json
from datetime import date, timedelta


def test_savings_goal_api_success(client, auth_headers):
    """Тестирование успешного расчета цели сбережений через API."""
    # Подготовка данных для запроса
    future_date = (date.today() + timedelta(days=365)
                   ).isoformat()  # Дата через год

    request_data = {
        'target_amount': '10000.00',
        'target_date': future_date,
        'current_savings': '1000.00'
    }

    # Выполнение запроса с авторизацией
    response = client.post(
        '/api/v1/calculator/savings-goal',
        json=request_data,
        headers=auth_headers
    )

    # Проверка ответа
    assert response.status_code == 200

    data = json.loads(response.data)

    # Проверка структуры ответа
    assert 'target_amount' in data
    assert 'current_savings' in data
    assert 'target_date' in data
    assert 'amount_to_save' in data
    assert 'months_remaining' in data
    assert 'required_monthly_savings' in data

    # Проверка значений
    assert data['target_amount'] == '10000.00'
    assert data['current_savings'] == '1000.00'
    assert data['target_date'] == future_date
    assert data['amount_to_save'] == '9000.00'

    # Месяцы должны быть примерно 12 (может быть 11-13 в зависимости от точной даты)
    assert 11 <= data['months_remaining'] <= 13


def test_savings_goal_api_validation_error(client, auth_headers):
    """Тестирование обработки ошибок валидации входных данных."""
    # Неверный формат суммы
    invalid_request = {
        'target_amount': 'not-a-number',
        'target_date': (date.today() + timedelta(days=365)).isoformat(),
        'current_savings': '1000.00'
    }

    response = client.post(
        '/api/v1/calculator/savings-goal',
        json=invalid_request,
        headers=auth_headers
    )

    assert response.status_code == 400
    assert 'message' in json.loads(response.data)


def test_savings_goal_api_date_error(client, auth_headers):
    """Тестирование обработки ошибок с датой."""
    # Дата в прошлом
    past_date_request = {
        'target_amount': '10000.00',
        'target_date': (date.today() - timedelta(days=1)).isoformat(),
        'current_savings': '1000.00'
    }

    response = client.post(
        '/api/v1/calculator/savings-goal',
        json=past_date_request,
        headers=auth_headers
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert 'future' in data['message']


def test_savings_goal_api_goal_reached(client, auth_headers):
    """Тестирование случая, когда цель уже достигнута."""
    request_data = {
        'target_amount': '1000.00',
        'target_date': (date.today() + timedelta(days=30)).isoformat(),
        'current_savings': '1500.00'  # Больше целевой суммы
    }

    response = client.post(
        '/api/v1/calculator/savings-goal',
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['amount_to_save'] == '0.00'
    assert data['months_remaining'] == 0
    assert data['required_monthly_savings'] == '0.00'
    assert 'message' in data
    assert 'Goal already reached' in data['message']


def test_savings_goal_api_unauthorized(client):
    """Тестирование доступа без авторизации."""
    request_data = {
        'target_amount': '10000.00',
        'target_date': (date.today() + timedelta(days=365)).isoformat(),
        'current_savings': '1000.00'
    }

    # Запрос без авторизационных заголовков
    response = client.post(
        '/api/v1/calculator/savings-goal',
        json=request_data
    )

    # Должен быть отказ в доступе
    assert response.status_code == 401
