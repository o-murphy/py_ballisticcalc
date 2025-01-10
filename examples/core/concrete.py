from generics.engine import BaseEngine, BaseEngineConfigDict, BaseEngineConfig
from generics.interface import Interface
from typing_extensions import NamedTuple


# Define a specialized TypedDict for ConcreteEngineConfig
class ConcreteEngineConfigDict(BaseEngineConfigDict):
    # config_param: str  # Specific field for this config type (can add more fields as necessary)
    config_param: str


# Concrete EngineConfig class that implements from_dict
class ConcreteEngineConfig(BaseEngineConfig[ConcreteEngineConfigDict]):
    config_param: str

    @staticmethod
    def from_dict(d: ConcreteEngineConfigDict) -> 'ConcreteEngineConfig':
        return ConcreteEngineConfig(
            d['config_param'],
        )


# Concrete Engine class
class ConcreteEngine(BaseEngine):
    def __init__(self, config: ConcreteEngineConfig) -> None:
        super().__init__(config)


i = Interface(ConcreteEngine)
print(i)
