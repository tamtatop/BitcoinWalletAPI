from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, NoReturn

from fastapi import HTTPException


@dataclass
class ErrorFormat:
    status_code: int
    error_message: str


@dataclass
class ErrorFormatter:
    error_format: Dict[Enum, ErrorFormat]

    def raise_http_exception(self, error: Enum) -> NoReturn:
        if error not in self.error_format:
            raise HTTPException(
                status_code=400, detail="Undocumented error, contact developers"
            )
        raise HTTPException(
            status_code=self.error_format[error].status_code,
            detail=self.error_format[error].error_message,
        )


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
