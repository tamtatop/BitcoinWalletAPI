from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, NoReturn, Union

from fastapi import HTTPException
from pydantic import BaseModel


@dataclass
class ErrorFormat:
    status_code: int
    error_message: str


class ErrorModel(BaseModel):
    detail: str


UNDOCUMENTED_ERROR_CODE = 400
UNDOCUMENTER_ERROR_MESSAGE = "Undocumented error, contact developers"


@dataclass
class ErrorFormatter:
    error_format: Dict[Enum, ErrorFormat]

    def raise_http_exception(self, error: Enum) -> NoReturn:
        if error not in self.error_format:
            raise HTTPException(
                status_code=UNDOCUMENTED_ERROR_CODE, detail=UNDOCUMENTER_ERROR_MESSAGE
            )
        raise HTTPException(
            status_code=self.error_format[error].status_code,
            detail=self.error_format[error].error_message,
        )

    def responses(self) -> Dict[Union[int, str], Dict[str, Any]]:
        d: Dict[Union[int, str], Dict[str, Any]] = {UNDOCUMENTED_ERROR_CODE: {
            "description": UNDOCUMENTER_ERROR_MESSAGE,
            "model": ErrorModel,
        }}
        for v in self.error_format.values():
            d[v.status_code] = {"description": v.error_message, "model": ErrorModel}
        return d


@dataclass
class ErrorFormatterBuilder:
    error_format: Dict[Enum, ErrorFormat] = field(default_factory=lambda: {})

    def add_error(
        self, error_type: Enum, error_message: str
    ) -> "ErrorFormatterBuilder":
        self.add_error_with_status_code(error_type, error_message, 400)
        return self

    def add_error_with_status_code(
        self, error_type: Enum, error_message: str, error_status_code: int
    ) -> "ErrorFormatterBuilder":
        self.error_format[error_type] = ErrorFormat(error_status_code, error_message)
        return self

    def build(self) -> ErrorFormatter:
        return ErrorFormatter(self.error_format)
