class DomainError(Exception):
    """Excepción base para los errores del dominio."""
    pass


class InvalidClientNameError(DomainError):
    """Se produce cuando el nombre del cliente no es válido."""
    pass


class ServiceNotAllowedError(DomainError):
    """Se produce cuando el servicio solicitado no está permitido."""
    pass


class InvalidDurationError(DomainError):
    """Se produce cuando la duración de la reserva no es válida."""
    pass


class InvalidReservationDateError(DomainError):
    """Se produce cuando la fecha de la reserva no es válida."""
    pass


class InvalidScheduleError(DomainError):
    """Se produce cuando el horario de la reserva no es válido."""
    pass


class DuplicateReservationError(DomainError):
    """Se produce cuando la reserva ya existe."""
    pass