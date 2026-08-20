from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class Reservation:
    """
    Representa una reserva ya validada y confirmada.
    Es inmutable (frozen) porque una vez creada no debería
    modificarse; cualquier cambio implica crear una nueva reserva.
    """
    customer_name: str
    service: str
    reservation_date: date
    reservation_time: time
    duration: int
    confirmation_code: str
    status: str = "confirmada"


class ReservationRepository:
    """
    Repositorio en memoria para reservas.

    Sustituye temporalmente una base de datos real, permitiendo que
    las pruebas sean rápidas e independientes entre sí. No usa
    estado global: cada instancia mantiene su propia lista interna,
    por lo que cada prueba puede crear un repositorio nuevo y limpio.
    """

    def __init__(self) -> None:
        self._reservations: list[Reservation] = []

    def exists(self, reservation_date: date, reservation_time: time) -> bool:
        """
        RN-08: comprueba si ya existe una reserva para una fecha
        y hora determinadas.
        """
        return any(
            r.reservation_date == reservation_date
            and r.reservation_time == reservation_time
            for r in self._reservations
        )

    def save(self, reservation: Reservation) -> Reservation:
        """Guarda una reserva y la devuelve."""
        self._reservations.append(reservation)
        return reservation

    def list_all(self) -> list[Reservation]:
        """
        Lista las reservas almacenadas.
        Devuelve una copia para que quien la reciba no pueda
        mutar el estado interno del repositorio directamente.
        """
        return list(self._reservations)