from typing import Dict, Any, Union, Tuple, Optional
from flask import current_app
from flask_restx import abort
import logging
from marshmallow import ValidationError as MarshmallowValidationError

# Настройка логгера
logger = logging.getLogger(__name__)


def handle_validation_error(error: MarshmallowValidationError,
                            status_code: int = 400) -> Tuple[Dict[str, Any], int]:
    """
    Обработчик ошибок валидации Marshmallow.

    Args:
        error: Объект ошибки валидации.
        status_code: HTTP код состояния (по умолчанию 400).

    Returns:
        Tuple с сообщением об ошибке и статус-кодом.
    """
    return {'message': error.messages}, status_code


def handle_value_error(error: ValueError,
                       status_code: int = 400,
                       log_error: bool = False,
                       user_id: Optional[int] = None) -> Tuple[Dict[str, Any], int]:
    """
    Обработчик ошибок типа ValueError.

    Args:
        error: Объект ошибки ValueError.
        status_code: HTTP код состояния (по умолчанию 400).
        log_error: Нужно ли логировать ошибку.
        user_id: ID пользователя для логирования (опционально).

    Returns:
        Tuple с сообщением об ошибке и статус-кодом.
    """
    if log_error:
        if user_id:
            logger.warning(f"ValueError for user {user_id}: {str(error)}")
        else:
            logger.warning(f"ValueError: {str(error)}")

    return {'message': str(error)}, status_code


def handle_exception(error: Exception,
                     endpoint_name: str,
                     user_id: Optional[int] = None,
                     status_code: int = 500) -> None:
    """
    Обработчик непредвиденных исключений с логированием и abort.

    Args:
        error: Объект исключения.
        endpoint_name: Имя эндпоинта, где произошла ошибка.
        user_id: ID пользователя (опционально).
        status_code: HTTP код состояния (по умолчанию 500).
    """
    error_message = f"Error in {endpoint_name}"
    if user_id:
        error_message += f" for user {user_id}"

    current_app.logger.error(
        f"{error_message}: {str(error)}",
        exc_info=True
    )

    abort(status_code, message="An internal server error occurred.")


# Функция для логирования операций
def log_operation(operation_type: str,
                  resource_type: str,
                  resource_id: Optional[Union[int, str]] = None,
                  user_id: Optional[int] = None,
                  details: Optional[Dict[str, Any]] = None) -> None:
    """
    Логирует операцию в системе.

    Args:
        operation_type: Тип операции (create, read, update, delete).
        resource_type: Тип ресурса (transaction, budget, category, etc).
        resource_id: ID ресурса (опционально).
        user_id: ID пользователя (опционально).
        details: Дополнительная информация (опционально).
    """
    log_message = f"{operation_type.upper()} {resource_type}"

    if resource_id:
        log_message += f" #{resource_id}"

    if user_id:
        log_message += f" by user #{user_id}"

    if details:
        log_message += f" - {details}"

    logger.info(log_message)
