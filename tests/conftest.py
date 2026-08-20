from datetime import date, time, timedelta

import pytest

from app.repositories import ReservationRepository
from app.reservation_service import ReservationService


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

@pytest.fixture
def fixed_confirmation_code_generator():
    """
    Dependencia controlable para generar el código de confirmación.
    Es una función pequeña que siempre devuelve el mismo valor, así
    las pruebas son predecibles: no se genera ningún UUID, número
    aleatorio ni timestamp real dentro de las pruebas ni del servicio.
    """
    def _generate() -> str:
        return "FIXED-CODE"

    return _generate


@pytest.fixture
def repository() -> ReservationRepository:
    """Repositorio en memoria, limpio, para cada prueba."""
    return ReservationRepository()


@pytest.fixture
def reservation_service(repository, fixed_confirmation_code_generator) -> ReservationService:
    """ReservationService con sus dependencias inyectadas y controladas."""
    return ReservationService(repository, fixed_confirmation_code_generator)


@pytest.fixture
def valid_reservation_data(reference_date) -> dict:
    """Conjunto mínimo de datos válidos para crear una reserva."""
    return {
        "customer_name": "Ana Torres",
        "service": "asesoria",
        "reservation_date": reference_date,
        "reservation_time": time(9, 0),
        "duration": 30,
    }