from datetime import date, timedelta

import pytest


@pytest.fixture
def reference_date() -> date:
    """
    Fecha 'actual' fija y controlada para las pruebas.
    Se eligió un miércoles (2024-06-05) para poder calcular
    días de semana y fines de semana de forma predecible,
    sin depender de datetime.now().
    """
    return date(2024, 6, 5)  # miércoles


@pytest.fixture
def next_saturday(reference_date) -> date:
    """El sábado inmediatamente después de reference_date."""
    days_until_saturday = (5 - reference_date.weekday()) % 7
    return reference_date + timedelta(days=days_until_saturday)


@pytest.fixture
def next_sunday(reference_date) -> date:
    """El domingo inmediatamente después de reference_date."""
    days_until_sunday = (6 - reference_date.weekday()) % 7
    return reference_date + timedelta(days=days_until_sunday)