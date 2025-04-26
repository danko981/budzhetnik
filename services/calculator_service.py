from datetime import date
from decimal import Decimal, ROUND_UP, InvalidOperation
from dateutil.relativedelta import relativedelta  # Для расчета разницы в месяцах
from typing import Dict, Union, Optional, Any


def calculate_required_savings(target_amount: Decimal, target_date: date,
                               current_savings: Optional[Decimal] = Decimal('0.00')) -> Dict[str, Any]:
    """
    Рассчитывает необходимую ежемесячную экономию для достижения финансовой цели.

    Args:
        target_amount: Целевая сумма.
        target_date: Дата достижения цели.
        current_savings: Текущие накопления (по умолчанию 0).

    Returns:
        Словарь с результатами расчета:
        {
            "target_amount": "...",
            "current_savings": "...",
            "target_date": "...",
            "amount_to_save": "...",
            "months_remaining": ...,
            "required_monthly_savings": "..." | null (if not applicable),
            "message": "..." (optional)
        }

    Raises:
        ValueError: Если входные данные не проходят валидацию или произошла ошибка расчета.
    """
    today = date.today()

    # --- Валидация входных данных ---
    if not isinstance(target_amount, Decimal):
        try:
            target_amount = Decimal(str(target_amount))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("Invalid target amount format.")

    if not isinstance(current_savings, Decimal):
        try:
            current_savings = Decimal(str(current_savings))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("Invalid current savings format.")

    if not isinstance(target_date, date):
        try:
            # Пробуем преобразовать строку даты
            if isinstance(target_date, str):
                target_date = date.fromisoformat(target_date)
            else:
                raise ValueError(
                    "Target date must be a date object or ISO format string.")
        except ValueError:
            raise ValueError("Invalid target date format. Use YYYY-MM-DD.")

    if target_amount <= 0:
        raise ValueError("Target amount must be positive.")
    if current_savings < 0:
        raise ValueError("Current savings cannot be negative.")
    if target_date <= today:
        raise ValueError("Target date must be in the future.")
    # ---------------------------------

    # Проверка достижения цели
    if current_savings >= target_amount:
        # Цель уже достигнута или превышена
        return {
            "target_amount": str(target_amount),
            "current_savings": str(current_savings),
            "target_date": target_date.isoformat(),
            "amount_to_save": str(Decimal('0.00')),
            "months_remaining": 0,
            "required_monthly_savings": str(Decimal('0.00')),
            "message": "Goal already reached or exceeded."
        }

    # Расчеты
    amount_to_save = target_amount - current_savings

    # Расчет количества полных месяцев до цели
    delta = relativedelta(target_date, today)
    # Учитываем дни: если до целевой даты меньше месяца, считаем как 1 месяц для расчета
    months_remaining = delta.years * 12 + delta.months
    if delta.days > 0 or (delta.years == 0 and delta.months == 0):
        # Если есть остаток дней или цель в текущем месяце, добавляем месяц
        months_remaining += 1

    if months_remaining <= 0:
        # Это не должно произойти из-за проверки target_date > today, но на всякий случай
        raise ValueError("Calculation error: non-positive months remaining.")

    # Расчет необходимой ежемесячной экономии
    # Округляем вверх до копеек (или центов)
    required_monthly_savings = (
        amount_to_save / Decimal(months_remaining)).quantize(Decimal('0.01'), rounding=ROUND_UP)

    return {
        "target_amount": str(target_amount),
        "current_savings": str(current_savings),
        "target_date": target_date.isoformat(),
        "amount_to_save": str(amount_to_save.quantize(Decimal('0.01'))),
        "months_remaining": months_remaining,
        "required_monthly_savings": str(required_monthly_savings)
    }


# Пример использования (для тестирования)
if __name__ == '__main__':
    try:
        target = Decimal('10000.00')
        current = Decimal('500.00')
        future_date = date.today() + relativedelta(years=1, months=6)
        result = calculate_required_savings(target, future_date, current)
        print(result)

        # Пример: цель достигнута
        result_reached = calculate_required_savings(
            Decimal('500'), date.today() + relativedelta(months=1), Decimal('600'))
        print(result_reached)

        # Пример: ошибка даты
        # result_err = calculate_required_savings(target, date.today(), current)
        # print(result_err)
    except ValueError as e:
        print(f"Error: {e}")
