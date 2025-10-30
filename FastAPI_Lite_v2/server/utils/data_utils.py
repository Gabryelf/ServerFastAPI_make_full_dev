from datetime import datetime
from typing import Any, Dict


def convert_datetime_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


def prepare_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    return convert_datetime_fields(user_data)