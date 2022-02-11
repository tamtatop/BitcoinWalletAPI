from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from app.core.admin.interactor import GetStatisticsRequest, GetStatisticsResponse, AdminError
from app.core.facade import WalletService
from app.infra.fastapi.dependables import get_core

error_message: Dict[AdminError, str] = {
    AdminError.INCORRECT_ADMIN_KEY: "Incorrect api key for admin"
}

admin_api = APIRouter()


@admin_api.get("/statistics")
def get_statistics(
        api_key: str,
        core: WalletService = Depends(get_core)
) -> GetStatisticsResponse:
    request = GetStatisticsRequest(api_key)

    get_statistics_response = core.get_statistics(request)

    if get_statistics_response.is_ok():
        return get_statistics_response.value
    else:
        raise HTTPException(
            status_code=400, detail=error_message[get_statistics_response.value]
        )
