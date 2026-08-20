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

    def test_creacion_valida_conserva_los_datos_de_la_reserva(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        # Act
        result = reservation_service.create(valid_reservation_data, reference_date)

        # Assert
        assert result.customer_name == "Ana Torres"
        assert result.service == "asesoria"
        assert result.duration == 30

    def test_creacion_valida_devuelve_reserva_con_estado_confirmada(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        # Act
        result = reservation_service.create(valid_reservation_data, reference_date)

        # Assert
        assert result.status == "confirmada"  # RN-09

    def test_creacion_valida_usa_el_codigo_del_generador_inyectado(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        # Act
        result = reservation_service.create(valid_reservation_data, reference_date)

        # Assert
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

    def test_servicio_con_mayusculas_y_espacios_se_normaliza_en_la_reserva_creada(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        # Arrange
        data = dict(valid_reservation_data, service="  ASESORIA  ")

        # Act
        result = reservation_service.create(data, reference_date)

        # Assert
        assert result.service == "asesoria"

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
        # Arrange
        data = dict(valid_reservation_data, customer_name="Al")

        # Act & Assert
        with pytest.raises(InvalidClientNameError):
            reservation_service.create(data, reference_date)

    def test_servicio_invalido_propaga_excepcion(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        # Arrange
        data = dict(valid_reservation_data, service="consultoria")

        # Act & Assert
        with pytest.raises(ServiceNotAllowedError):
            reservation_service.create(data, reference_date)

    def test_duracion_invalida_propaga_excepcion(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        # Arrange
        data = dict(valid_reservation_data, duration=45)

        # Act & Assert
        with pytest.raises(InvalidDurationError):
            reservation_service.create(data, reference_date)

    def test_fecha_fin_de_semana_propaga_excepcion(
        self, reservation_service, valid_reservation_data, reference_date, next_saturday
    ):
        # Arrange
        data = dict(valid_reservation_data, reservation_date=next_saturday)

        # Act & Assert
        with pytest.raises(InvalidReservationDateError):
            reservation_service.create(data, reference_date)

    def test_hora_fuera_de_horario_propaga_excepcion(
        self, reservation_service, valid_reservation_data, reference_date
    ):
        # Arrange
        data = dict(valid_reservation_data, reservation_time=time(7, 0))

        # Act & Assert
        with pytest.raises(InvalidScheduleError):
            reservation_service.create(data, reference_date)

    # --- Si una validación falla, no debe guardarse ninguna reserva ---
    # (parametrizado: recorre varios campos inválidos con la misma prueba)

    @pytest.mark.parametrize(
        "overrides, expected_exception",
        [
            ({"customer_name": "Al"}, InvalidClientNameError),
            ({"service": "consultoria"}, ServiceNotAllowedError),
            ({"duration": 45}, InvalidDurationError),
            ({"reservation_time": time(7, 0)}, InvalidScheduleError),
        ],
    )
    def test_datos_invalidos_no_guardan_ninguna_reserva(
        self,
        reservation_service,
        repository,
        valid_reservation_data,
        reference_date,
        overrides,
        expected_exception,
    ):
        # Arrange
        data = dict(valid_reservation_data, **overrides)

        # Act & Assert
        with pytest.raises(expected_exception):
            reservation_service.create(data, reference_date)

        assert repository.list_all() == []

    def test_fecha_invalida_no_guarda_ninguna_reserva(
        self, reservation_service, repository, valid_reservation_data,
        reference_date, next_saturday,
    ):
        # Arrange
        data = dict(valid_reservation_data, reservation_date=next_saturday)

        # Act & Assert
        with pytest.raises(InvalidReservationDateError):
            reservation_service.create(data, reference_date)

        assert repository.list_all() == []

    def test_reserva_duplicada_no_agrega_una_segunda_reserva(
        self, reservation_service, repository, valid_reservation_data, reference_date
    ):
        # Arrange
        reservation_service.create(valid_reservation_data, reference_date)

        # Act & Assert
        with pytest.raises(DuplicateReservationError):
            reservation_service.create(valid_reservation_data, reference_date)

        assert len(repository.list_all()) == 1

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