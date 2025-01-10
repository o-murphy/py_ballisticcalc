from typing_extensions import Type, TypeVar, Optional, Generic
from dataclasses import dataclass, field

from examples.core.generics.engine import BaseEngine, TConfigDict

# Ensure TConfigDict is bound in the Interface class
TEngine = TypeVar("TEngine", bound=BaseEngine)  # Engine type is bound to BaseEngine with TConfigDict

# Interface class that expects an engine and config
@dataclass
class Interface(Generic[TEngine[TConfigDict], TConfigDict]):
    _engine: Type[TEngine]  # The class/type of a BaseEngine subclass
    _instance: Optional[TEngine] = field(default=None, init=False)  # Instance of the engine
    _config: TConfigDict  # Expected configuration for the engine

    def create_instance(self) -> None:
        """Creates an instance of the engine with the provided config."""
        self._instance = self._engine(self._config)  # Instantiate engine

