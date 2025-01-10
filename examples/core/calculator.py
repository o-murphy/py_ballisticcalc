from dataclasses import dataclass
from typing_extensions import Generic

from examples.core.generics.interface import Interface, TEngine, TConfigDict


@dataclass
class Calculator(Interface[TEngine, TConfigDict], Generic[TEngine, TConfigDict]):
    pass


"""
Other approach to create custom interface
custom_interface = Interface[CustomEngine, CustomConfig](
    _engine=CustomEngine,
    _config={"param1": 100, "param2": "test"}  # This must match CustomConfig
)
"""
