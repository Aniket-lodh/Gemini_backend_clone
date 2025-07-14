from fastapi.responses import JSONResponse
from typing import Any, Dict
from fastapi import status


def format_response(
    success: bool = True,
    message: str = "",
    status_code: int = status.HTTP_200_OK,
    data=None,
    additional_data: Dict[str, Any] = None,
) -> JSONResponse:
    """
    A reusable utility function for creating JSON responses.

    :param success: A boolean value indicating if api executed successfully or not.
    :param message: A message to include in the response (e.g., success/failure message).
    :param status_code: HTTP status code (default: 200).
    :param data: The response body (default: None).
    :param additional_data: A dictionary of additional data to include in the response body (default: None).
    For additional_data to get included in response body, data has to be a dict.
    :return: A JSONResponse object with the provided data.

    ```python
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/user_plans")
    async def get_user_plans():
        # Suppose serialized_cur_user_plans is your data
        serialized_cur_user_plans = {"plan": "Basic", "valid_until": "2025-01-01"}

        return format_response(
            message="Fetched User plans",
            status=200,
            data=serialized_cur_user_plans
        )

    ```
    """
    try:
        response_content = {
            "message": message,
            "success": (
                success
                if isinstance(success, bool)
                else (True if status_code in range(200, 300) else False)
            ),
            "status_code": status_code,
            "data": data or {},
        }
        if additional_data and isinstance(data, dict):
            response_content["body"].update(additional_data)

        return JSONResponse(
            content=response_content,
            status_code=status_code,
        )
    except Exception as e:
        raise Exception("Couldn't construct JSONResponse | ERROR:: ", str(e))
