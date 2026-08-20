from datetime import timedelta, time

import pytest

from app.exceptions import (
    InvalidClientNameError,
    ServiceNotAllowedError,
    InvalidDurationError,
    InvalidReservationDateError,
    InvalidScheduleError,
)
from app.validators import (
    validate_customer_name,
    validate_service,
    validate_duration,
    validate_reservation_date,
    validate_reservation_time,
)

class TestValidateCustomerName:
    # --- Casos positivos ---

    def test_nombre_valido_se_retorna_sin_cambios(self):
        # Arrange
        name = "Ana"

        # Act
        result = validate_customer_name(name)

        # Assert
        assert result == "Ana"

    def test_nombre_con_espacios_externos_se_normaliza(self):
        # Arrange
        name = "  Carlos Perez  "

        # Act
        result = validate_customer_name(name)

        # Assert
        assert result == "Carlos Perez"

    # --- Caso de frontera ---

    def test_nombre_con_exactamente_3_caracteres_es_valido(self):
        # Arrange
        name = "Luz"

        # Act
        result = validate_customer_name(name)

        # Assert
        assert result == "Luz"

    def test_nombre_con_espacios_que_al_recortar_llega_a_3_es_valido(self):
        # Arrange
        name = "  Luz  "

        # Act
        result = validate_customer_name(name)

        # Assert
        assert result == "Luz"

    # --- Casos negativos ---

    def test_nombre_con_menos_de_3_caracteres_lanza_excepcion(self):
        # Arrange
        name = "Al"

        # Act & Assert
        with pytest.raises(InvalidClientNameError):
            validate_customer_name(name)

    def test_nombre_que_al_recortar_queda_por_debajo_del_minimo(self):
        # Arrange
        name = "  Al  "

        # Act & Assert
        with pytest.raises(InvalidClientNameError):
            validate_customer_name(name)

    def test_nombre_vacio_lanza_excepcion(self):
        # Arrange
        name = ""

        # Act & Assert
        with pytest.raises(InvalidClientNameError):
            validate_customer_name(name)

    def test_nombre_solo_con_espacios_lanza_excepcion(self):
        # Arrange
        name = "   "

        # Act & Assert
        with pytest.raises(InvalidClientNameError):
            validate_customer_name(name)

    def test_nombre_none_lanza_excepcion(self):
        # Arrange
        name = None

        # Act & Assert
        with pytest.raises(InvalidClientNameError):
            validate_customer_name(name)

class TestValidateService:
    # --- Casos positivos (parametrizados) ---

    @pytest.mark.parametrize(
        "service",
        ["asesoria", "soporte", "demostracion"],
    )
    def test_servicio_permitido_se_retorna_normalizado(self, service):
        # Arrange (service viene del parametrize)

        # Act
        result = validate_service(service)

        # Assert
        assert result == service

    def test_servicio_con_mayusculas_se_normaliza_a_minusculas(self):
        # Arrange
        service = "ASESORIA"

        # Act
        result = validate_service(service)

        # Assert
        assert result == "asesoria"

    def test_servicio_con_espacios_externos_se_normaliza(self):
        # Arrange
        service = "  soporte  "

        # Act
        result = validate_service(service)

        # Assert
        assert result == "soporte"

    # --- Casos negativos ---

    def test_servicio_no_permitido_lanza_excepcion(self):
        # Arrange
        service = "consultoria"

        # Act & Assert
        with pytest.raises(ServiceNotAllowedError):
            validate_service(service)

    def test_servicio_vacio_lanza_excepcion(self):
        # Arrange
        service = ""

        # Act & Assert
        with pytest.raises(ServiceNotAllowedError):
            validate_service(service)

    def test_servicio_none_lanza_excepcion(self):
        # Arrange
        service = None

        # Act & Assert
        with pytest.raises(ServiceNotAllowedError):
            validate_service(service)

class TestValidateDuration:
    # --- Casos positivos (parametrizados) ---

    @pytest.mark.parametrize("duration", [30, 60])
    def test_duracion_permitida_se_retorna_sin_cambios(self, duration):
        # Arrange (duration viene del parametrize)

        # Act
        result = validate_duration(duration)

        # Assert
        assert result == duration

    # --- Casos de frontera / negativos ---

    def test_duracion_menor_a_30_lanza_excepcion(self):
        # Arrange
        duration = 29

        # Act & Assert
        with pytest.raises(InvalidDurationError):
            validate_duration(duration)

    def test_duracion_entre_30_y_60_lanza_excepcion(self):
        # Arrange
        duration = 45

        # Act & Assert
        with pytest.raises(InvalidDurationError):
            validate_duration(duration)

    def test_duracion_mayor_a_60_lanza_excepcion(self):
        # Arrange
        duration = 90

        # Act & Assert
        with pytest.raises(InvalidDurationError):
            validate_duration(duration)

    def test_duracion_negativa_lanza_excepcion(self):
        # Arrange
        duration = -30

        # Act & Assert
        with pytest.raises(InvalidDurationError):
            validate_duration(duration)

    def test_duracion_cero_lanza_excepcion(self):
        # Arrange
        duration = 0

        # Act & Assert
        with pytest.raises(InvalidDurationError):
            validate_duration(duration)

    def test_duracion_none_lanza_excepcion(self):
        # Arrange
        duration = None

        # Act & Assert
        with pytest.raises(InvalidDurationError):
            validate_duration(duration)

    def test_duracion_como_texto_lanza_excepcion(self):
        # Arrange
        duration = "30"

        # Act & Assert
        with pytest.raises(InvalidDurationError):
            validate_duration(duration)

    def test_duracion_booleana_lanza_excepcion(self):
        # Arrange
        duration = True

        # Act & Assert
        with pytest.raises(InvalidDurationError):
            validate_duration(duration)

class TestValidateReservationDate:
    # --- Casos positivos ---

    def test_fecha_igual_a_la_actual_y_dia_habil_es_valida(self, reference_date):
        # Arrange
        # reference_date es miércoles (día hábil) -> misma fecha, no es "anterior"
        reservation_date = reference_date

        # Act
        result = validate_reservation_date(reservation_date, reference_date)

        # Assert
        assert result == reservation_date

    def test_fecha_futura_en_dia_habil_es_valida(self, reference_date):
        # Arrange
        reservation_date = reference_date + timedelta(days=1)  # jueves

        # Act
        result = validate_reservation_date(reservation_date, reference_date)

        # Assert
        assert result == reservation_date

    # --- Casos negativos: RN-04 (fecha anterior) ---

    def test_fecha_anterior_a_la_actual_lanza_excepcion(self, reference_date):
        # Arrange
        reservation_date = reference_date - timedelta(days=1)

        # Act & Assert
        with pytest.raises(InvalidReservationDateError):
            validate_reservation_date(reservation_date, reference_date)

    # --- Casos negativos: RN-05 (solo lunes a viernes) ---

    def test_fecha_en_sabado_lanza_excepcion(self, reference_date, next_saturday):
        # Act & Assert
        with pytest.raises(InvalidReservationDateError):
            validate_reservation_date(next_saturday, reference_date)

    def test_fecha_en_domingo_lanza_excepcion(self, reference_date, next_sunday):
        # Act & Assert
        with pytest.raises(InvalidReservationDateError):
            validate_reservation_date(next_sunday, reference_date)

    # --- Casos None ---

    def test_fecha_de_reserva_none_lanza_excepcion(self, reference_date):
        # Act & Assert
        with pytest.raises(InvalidReservationDateError):
            validate_reservation_date(None, reference_date)

    def test_fecha_actual_none_lanza_excepcion(self, reference_date):
        # Act & Assert
        with pytest.raises(InvalidReservationDateError):
            validate_reservation_date(reference_date, None)

class TestValidateReservationTime:
    # --- Casos positivos ---

    def test_hora_apertura_exacta_con_duracion_30_es_valida(self):
        # Arrange
        reservation_time = time(8, 0)
        duration = 30

        # Act
        result = validate_reservation_time(reservation_time, duration)

        # Assert
        assert result == reservation_time

    def test_hora_que_termina_exactamente_a_las_17_es_valida(self):
        # Arrange
        reservation_time = time(16, 0)
        duration = 30

        # Act
        result = validate_reservation_time(reservation_time, duration)

        # Assert
        assert result == reservation_time

    def test_hora_intermedia_del_dia_es_valida(self):
        # Arrange
        reservation_time = time(12, 30)
        duration = 30

        # Act
        result = validate_reservation_time(reservation_time, duration)

        # Assert
        assert result == reservation_time

    # --- Casos de frontera / negativos: RN-06 (inicio) ---

    def test_hora_antes_de_apertura_lanza_excepcion(self):
        # Arrange
        reservation_time = time(7, 59)
        duration = 30

        # Act & Assert
        with pytest.raises(InvalidScheduleError):
            validate_reservation_time(reservation_time, duration)

    # --- Casos de frontera / negativos: RN-07 (fin máximo 17:00) ---

    def test_hora_que_termina_pasadas_las_17_lanza_excepcion(self):
        # Arrange
        reservation_time = time(16, 1)
        duration = 60

        # Act & Assert
        with pytest.raises(InvalidScheduleError):
            validate_reservation_time(reservation_time, duration)

    def test_hora_muy_tarde_lanza_excepcion(self):
        # Arrange
        reservation_time = time(17, 0)
        duration = 30

        # Act & Assert
        with pytest.raises(InvalidScheduleError):
            validate_reservation_time(reservation_time, duration)

    # --- Casos None ---

    def test_hora_none_lanza_excepcion(self):
        # Act & Assert
        with pytest.raises(InvalidScheduleError):
            validate_reservation_time(None, 30)

    def test_duracion_none_lanza_excepcion(self):
        # Act & Assert
        with pytest.raises(InvalidScheduleError):
            validate_reservation_time(time(9, 0), None)