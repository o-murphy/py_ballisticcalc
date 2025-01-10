from abc import ABC
from typing import TypeVar, Protocol

from typing_extensions import TypedDict, Generic, Dict

# Define a generic type for Engine
TEngine = TypeVar('TEngine', bound='BaseEngine')
TConfigDict = TypeVar('TConfigDict', bound=Dict)


# Define the TypedDict for configuration
class BaseEngineConfigDict(TypedDict, Generic[TConfigDict]):
    # config_param: str  # Common field, can be overridden or extended by specific engine configs
    pass


# Define the BaseEngineConfig abstract base class
# Define the BaseEngineConfig protocol (interface)
class BaseEngineConfig(Protocol[TConfigDict]):

    @staticmethod
    def from_dict(d: TConfigDict) -> 'BaseEngineConfig':
        pass


# Define the BaseEngine abstract class
class BaseEngine(ABC):
    def __init__(self, config: BaseEngineConfig) -> None:
        self.config = config
