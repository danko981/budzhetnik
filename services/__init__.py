"""
Модуль сервисов для работы с бизнес-логикой приложения.
Использует современные практики доступа к данным через абстракцию ORM.
"""

from services.auth_service import AuthService
from services.base_service import BaseService
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from services.budget_service import BudgetService

__all__ = [
    'AuthService',
    'BaseService',
    'CategoryService',
    'TransactionService',
    'BudgetService'
]
