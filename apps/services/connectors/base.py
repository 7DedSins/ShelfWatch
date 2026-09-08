from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class RemoteLibrary:
    id: str
    name: str


@dataclass(frozen=True)
class HealthResult:
    ok: bool
    detail: str = ""


@dataclass(frozen=True)
class RemoteSeries:
    id: str
    name: str
    library_id: str


class ConnectorError(Exception):
    pass


class ServiceUnavailable(ConnectorError):
    pass


class ServiceAuthFailed(ConnectorError):
    pass


class ServiceBadResponse(ConnectorError):
    pass


class BaseConnector(ABC):
    @abstractmethod
    def list_series(self, library_id: str) -> Iterator[RemoteSeries]: ...

    @abstractmethod
    def list_libraries(self) -> list[RemoteLibrary]: ...

    @abstractmethod
    def health(self) -> HealthResult: ...

    def active_scans(self) -> list:
        return []
