from datetime import date
from typing import Callable

from app.exceptions import DuplicateReservationError
from app.repositories import Reservation, ReservationRepository
from app.validators import (
    validate_customer_name,
    validate_service,
    validate_duration,
    validate_reservation_date,
    validate_reservation_time,
)


class ReservationService:
    """
    Orquesta la creación de una reserva: aplica las reglas de negocio
    (a través de los validadores), comprueba duplicados en el
    repositorio y persiste la reserva ya confirmada.

    Recibe sus dependencias por constructor (repositorio y generador
    de código de confirmación) para poder sustituirlas fácilmente
    en las pruebas, sin depender de una base de datos real ni de
    generación aleatoria dentro del propio servicio.
    """

    def __init__(
        self,
        repository: ReservationRepository,
        confirmation_code_generator: Callable[[], str],
    ) -> None:
        self._repository = repository
        self._confirmation_code_generator = confirmation_code_generator

    def create(self, data: dict, current_date: date) -> Reservation:
        """
        Aplica las reglas de negocio en orden coherente:
        1. Valida cada campo individual (RN-01 a RN-07).
        2. Comprueba que no exista ya una reserva en esa fecha/hora (RN-08).
        3. Genera el código de confirmación mediante la dependencia inyectada (RN-10).
        4. Construye la reserva como "confirmada" (RN-09), la guarda y la devuelve.
        """
        customer_name = validate_customer_name(data["customer_name"])
        service = validate_service(data["service"])
        duration = validate_duration(data["duration"])
        reservation_date = validate_reservation_date(
            data["reservation_date"], current_date
        )
        reservation_time = validate_reservation_time(
            data["reservation_time"], duration
        )

        if self._repository.exists(reservation_date, reservation_time):
            raise DuplicateReservationError(
                "Ya existe una reserva para la fecha y hora seleccionadas."
            )

        confirmation_code = self._confirmation_code_generator()

        reservation = Reservation(
            customer_name=customer_name,
            service=service,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            duration=duration,
            confirmation_code=confirmation_code,
        )

        return self._repository.save(reservation)