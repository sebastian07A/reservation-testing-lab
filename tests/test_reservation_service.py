from datetime import time

import pytest

from app.exceptions import (
    InvalidClientNameError,
    ServiceNotAllowedError,
    InvalidDurationError,
    InvalidReservationDateError,
    InvalidScheduleError,
    DuplicateReservationError,
)
from app.repositories import ReservationRepository
from app.reservation_service import ReservationService


class TestReservationServiceCreate:
    # --- Caso positivo principal ---

    def test_creacion_valida_devuelve_reserva_confirmada(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        # Act
        result = reservation_service.create(valid_reservation_data, reference_date)

        # Assert
        assert result.customer_name == "Ana Torres"
        assert result.service == "asesoria"
        assert result.duration == 30
        assert result.status == "confirmada"  # RN-09
        assert result.confirmation_code == "FIXED-CODE"  # RN-10

    def test_creacion_valida_guarda_la_reserva_en_el_repositorio(
        self, reservation_service, repository, valid_reservation_data, reference_date
    ):
        # Act
        result = reservation_service.create(valid_reservation_data, reference_date)

        # Assert
        assert repository.list_all() == [result]

    def test_nombre_con_espacios_se_normaliza_en_la_reserva_creada(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        # Arrange
        data = dict(valid_reservation_data, customer_name="  Ana Torres  ")

        # Act
        result = reservation_service.create(data, reference_date)

        # Assert
        assert result.customer_name == "Ana Torres"

    # --- RN-08: duplicados ---

    def test_reserva_duplicada_lanza_excepcion(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        # Arrange
        reservation_service.create(valid_reservation_data, reference_date)

        # Act & Assert
        with pytest.raises(DuplicateReservationError):
            reservation_service.create(valid_reservation_data, reference_date)

    def test_misma_fecha_hora_distinta_no_es_duplicado(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        # Arrange
        reservation_service.create(valid_reservation_data, reference_date)
        other_data = dict(valid_reservation_data, reservation_time=time(10, 0))

        # Act
        result = reservation_service.create(other_data, reference_date)

        # Assert
        assert result.reservation_time == time(10, 0)

    # --- Propagación de reglas de validación (RN-01 a RN-07) ---

    def test_nombre_invalido_propaga_excepcion(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        data = dict(valid_reservation_data, customer_name="Al")

        with pytest.raises(InvalidClientNameError):
            reservation_service.create(data, reference_date)

    def test_servicio_invalido_propaga_excepcion(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        data = dict(valid_reservation_data, service="consultoria")

        with pytest.raises(ServiceNotAllowedError):
            reservation_service.create(data, reference_date)

    def test_duracion_invalida_propaga_excepcion(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        data = dict(valid_reservation_data, duration=45)

        with pytest.raises(InvalidDurationError):
            reservation_service.create(data, reference_date)

    def test_fecha_fin_de_semana_propaga_excepcion(
        self, reservation_service, valid_reservation_data, reference_date, next_saturday
    ):
        data = dict(valid_reservation_data, reservation_date=next_saturday)

        with pytest.raises(InvalidReservationDateError):
            reservation_service.create(data, reference_date)

    def test_hora_fuera_de_horario_propaga_excepcion(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        data = dict(valid_reservation_data, reservation_time=time(7, 0))

        with pytest.raises(InvalidScheduleError):
            reservation_service.create(data, reference_date)

    # --- RN-10: el generador de código es una dependencia sustituible ---

    def test_generador_de_codigo_es_sustituible_por_otra_dependencia(
        self, repository, valid_reservation_data, reference_date
    ):
        # Arrange: un generador distinto al de la fixture por defecto
        service = ReservationService(repository, lambda: "OTRO-CODIGO")

        # Act
        result = service.create(valid_reservation_data, reference_date)

        # Assert
        assert result.confirmation_code == "OTRO-CODIGO"

    # --- Independencia entre pruebas / instancias ---

    def test_dos_servicios_con_repositorios_distintos_no_comparten_estado(
        self, fixed_confirmation_code_generator, valid_reservation_data, reference_date
    ):
        # Arrange
        repository_a = ReservationRepository()
        repository_b = ReservationRepository()
        service_a = ReservationService(repository_a, fixed_confirmation_code_generator)
        service_b = ReservationService(repository_b, fixed_confirmation_code_generator)

        # Act
        service_a.create(valid_reservation_data, reference_date)

        # Assert
        assert len(repository_a.list_all()) == 1
        assert len(repository_b.list_all()) == 0