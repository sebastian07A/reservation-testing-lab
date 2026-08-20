from datetime import date, datetime, time, timedelta

from app.exceptions import (
    InvalidClientNameError,
    ServiceNotAllowedError,
    InvalidDurationError,
    InvalidReservationDateError,
    InvalidScheduleError,
)

MIN_CUSTOMER_NAME_LENGTH = 3
ALLOWED_SERVICES = {"asesoria", "soporte", "demostracion"}
ALLOWED_DURATIONS = {30, 60}
# lunes=0 ... viernes=4 (según date.weekday())
ALLOWED_WEEKDAYS = {0, 1, 2, 3, 4}
OPENING_TIME = time(8, 0)
CLOSING_TIME = time(17, 0)


def validate_customer_name(name: str) -> str:
    """
    RN-01: El nombre del cliente debe tener mínimo 3 caracteres
    después de eliminar espacios al inicio y al final.
    """
    if name is None:
        raise InvalidClientNameError(
            "El nombre del cliente no puede ser nulo."
        )

    normalized_name = name.strip()

    if len(normalized_name) < MIN_CUSTOMER_NAME_LENGTH:
        raise InvalidClientNameError(
            f"El nombre del cliente debe tener al menos "
            f"{MIN_CUSTOMER_NAME_LENGTH} caracteres."
        )

    return normalized_name

def validate_service(service: str) -> str:
    """
    RN-02: Los servicios permitidos son: asesoria, soporte y demostracion.

    Normaliza el servicio (quita espacios y pasa a minúsculas) y
    comprueba que pertenezca al conjunto permitido.
    """
    if service is None:
        raise ServiceNotAllowedError(
            "El servicio no puede ser nulo."
        )

    normalized_service = service.strip().lower()

    if normalized_service not in ALLOWED_SERVICES:
        raise ServiceNotAllowedError(
            f"El servicio '{service}' no está permitido. "
            f"Servicios válidos: {', '.join(sorted(ALLOWED_SERVICES))}."
        )

    return normalized_service

def validate_duration(duration: int) -> int:
    """
    RN-03: La duración permitida es únicamente 30 o 60 minutos.
    """
    if duration is None:
        raise InvalidDurationError(
            "La duración no puede ser nula."
        )

    if isinstance(duration, bool) or not isinstance(duration, int):
        raise InvalidDurationError(
            "La duración debe ser un número entero de minutos."
        )

    if duration not in ALLOWED_DURATIONS:
        raise InvalidDurationError(
            f"La duración de {duration} minutos no es válida. "
            f"Duraciones permitidas: {sorted(ALLOWED_DURATIONS)}."
        )

    return duration

def validate_reservation_date(reservation_date: date, current_date: date) -> date:
    """
    RN-04: No se puede crear una reserva para una fecha anterior
    a la fecha actual recibida por el servicio.
    RN-05: Solo se permiten reservas de lunes a viernes.

    `current_date` se recibe como parámetro (no se calcula con
    datetime.now() dentro de la función) para que el validador sea
    puro y las pruebas puedan controlar la fecha "actual".
    """
    if reservation_date is None or current_date is None:
        raise InvalidReservationDateError(
            "La fecha de la reserva y la fecha actual no pueden ser nulas."
        )

    if reservation_date < current_date:
        raise InvalidReservationDateError(
            "No se puede reservar en una fecha anterior a la fecha actual."
        )

    if reservation_date.weekday() not in ALLOWED_WEEKDAYS:
        raise InvalidReservationDateError(
            "Solo se permiten reservas de lunes a viernes."
        )

    return reservation_date

def validate_reservation_time(reservation_time: time, duration: int) -> time:
    """
    RN-06: El horario de atención inicia a las 08:00.
    RN-07: La reserva debe finalizar máximo a las 17:00.

    Se combina con `duration` (ya validada por validate_duration)
    para calcular la hora de fin y comprobar que no exceda el cierre.
    """
    if reservation_time is None or duration is None:
        raise InvalidScheduleError(
            "La hora de la reserva y la duración no pueden ser nulas."
        )

    if reservation_time < OPENING_TIME:
        raise InvalidScheduleError(
            "El horario de atención inicia a las 08:00."
        )

    start_datetime = datetime.combine(date.min, reservation_time)
    end_datetime = start_datetime + timedelta(minutes=duration)

    if end_datetime.time() > CLOSING_TIME or end_datetime.day != date.min.day:
        raise InvalidScheduleError(
            "La reserva debe finalizar máximo a las 17:00."
        )

    return reservation_time