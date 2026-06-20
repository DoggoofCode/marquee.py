from .base import BankConnector


class ConnectorRegistry:
    def __init__(self) -> None:
        self._connectors: list[BankConnector] = []

    def register(self, connector: BankConnector) -> None:
        self._connectors.append(connector)

    @property
    def connectors(self) -> list[BankConnector]:
        return list(self._connectors)
