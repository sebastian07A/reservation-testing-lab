from datetime import date, time

from app.repositories import Reservation, ReservationRepository


def make_reservation(
    customer_name="Ana Torres",
    service="asesoria",
    reservation_date=date(2024, 6, 5),
    reservation_time=time(9, 0),
    duration=30,
    confirmation_code="ABC123",
) -> Reservation:
    """Helper para construir una Reservation de prueba con valores por defecto."""
    return Reservation(
        customer_name=customer_name,
        service=service,
        reservation_date=reservation_date,
        reservation_time=reservation_time,
        duration=duration,
        confirmation_code=confirmation_code,
    )


class TestReservationRepositoryExists:
    def test_repositorio_vacio_no_tiene_reservas(self):
        # Arrange
        repository = ReservationRepository()

        # Act
        result = repository.exists(date(2024, 6, 5), time(9, 0))

        # Assert
        assert result is False

    def test_existe_reserva_para_fecha_y_hora_guardadas(self):
        # Arrange
        repository = ReservationRepository()
        reservation = make_reservation(
            reservation_date=date(2024, 6, 5), reservation_time=time(9, 0)
        )
        repository.save(reservation)

        # Act
        result = repository.exists(date(2024, 6, 5), time(9, 0))

        # Assert
        assert result is True

    def test_no_existe_reserva_para_hora_distinta(self):
        # Arrange
        repository = ReservationRepository()
        reservation = make_reservation(
            reservation_date=date(2024, 6, 5), reservation_time=time(9, 0)
        )
        repository.save(reservation)

        # Act
        result = repository.exists(date(2024, 6, 5), time(10, 0))

        # Assert
        assert result is False

    def test_no_existe_reserva_para_fecha_distinta(self):
        # Arrange
        repository = ReservationRepository()
        reservation = make_reservation(
            reservation_date=date(2024, 6, 5), reservation_time=time(9, 0)
        )
        repository.save(reservation)

        # Act
        result = repository.exists(date(2024, 6, 6), time(9, 0))

        # Assert
        assert result is False


class TestReservationRepositorySave:
    def test_guardar_devuelve_la_misma_reserva(self):
        # Arrange
        repository = ReservationRepository()
        reservation = make_reservation()

        # Act
        result = repository.save(reservation)

        # Assert
        assert result == reservation

    def test_guardar_agrega_la_reserva_a_la_lista(self):
        # Arrange
        repository = ReservationRepository()
        reservation = make_reservation()

        # Act
        repository.save(reservation)

        # Assert
        assert repository.list_all() == [reservation]


class TestReservationRepositoryListAll:
    def test_repositorio_vacio_lista_vacia(self):
        # Arrange
        repository = ReservationRepository()

        # Act
        result = repository.list_all()

        # Assert
        assert result == []

    def test_lista_refleja_orden_de_guardado(self):
        # Arrange
        repository = ReservationRepository()
        first = make_reservation(reservation_time=time(9, 0))
        second = make_reservation(reservation_time=time(10, 0))
        repository.save(first)
        repository.save(second)

        # Act
        result = repository.list_all()

        # Assert
        assert result == [first, second]

    def test_list_all_devuelve_una_copia_independiente(self):
        # Arrange
        repository = ReservationRepository()
        repository.save(make_reservation())

        # Act
        result = repository.list_all()
        result.clear()

        # Assert: mutar la lista devuelta no debe afectar al repositorio
        assert len(repository.list_all()) == 1


class TestReservationRepositoryIndependence:
    def test_dos_instancias_no_comparten_estado(self):
        # Arrange
        repository_a = ReservationRepository()
        repository_b = ReservationRepository()

        # Act
        repository_a.save(make_reservation())

        # Assert
        assert len(repository_a.list_all()) == 1
        assert len(repository_b.list_all()) == 0