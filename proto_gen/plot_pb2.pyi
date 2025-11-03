from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AddAxisRequest(_message.Message):
    __slots__ = ("axis_id", "number_of_samples", "plot_title", "x_axis_title", "y_axis_title")
    AXIS_ID_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    PLOT_TITLE_FIELD_NUMBER: _ClassVar[int]
    X_AXIS_TITLE_FIELD_NUMBER: _ClassVar[int]
    Y_AXIS_TITLE_FIELD_NUMBER: _ClassVar[int]
    axis_id: int
    number_of_samples: int
    plot_title: str
    x_axis_title: str
    y_axis_title: str
    def __init__(self, axis_id: _Optional[int] = ..., number_of_samples: _Optional[int] = ..., plot_title: _Optional[str] = ..., x_axis_title: _Optional[str] = ..., y_axis_title: _Optional[str] = ...) -> None: ...

class streamPoint(_message.Message):
    __slots__ = ("axis_id", "value")
    AXIS_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    axis_id: int
    value: float
    def __init__(self, axis_id: _Optional[int] = ..., value: _Optional[float] = ...) -> None: ...
