from fastapi import APIRouter, Depends
from result.result import Ok

from app.core.admin.interactor import (
    AdminError,
    GetStatisticsRequest,
    GetStatisticsResponse,
)
from app.core.facade import WalletService
from app.infra.fastapi.dependables import get_core
from app.infra.fastapi.error_formatter import ErrorFormatterBuilder

error_formatter = (
    ErrorFormatterBuilder()
    .add_error_with_status_code(
        AdminError.INCORRECT_ADMIN_KEY, "Incorrect api key for admin", 410
    )
    .build()
)

admin_api = APIRouter()


@admin_api.get(
    "/statistics",
    response_model=GetStatisticsResponse,
    responses=error_formatter.responses(),
)
def get_statistics(
    admin_key: str, core: WalletService = Depends(get_core)
) -> GetStatisticsResponse:
    request = GetStatisticsRequest(admin_key)

    get_statistics_response = core.get_statistics(request)

    if isinstance(get_statistics_response, Ok):
        return get_statistics_response.value
    else:
        error_formatter.raise_http_exception(get_statistics_response.value)
