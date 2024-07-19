from typing import Union, Dict


class CustomException(Exception):
    def __init__(self, status_code: int, custom_status: str,  message: str, data: Union[Dict, None] = None):
        self.status_code = status_code
        self.custom_status = custom_status
        self.message = message
        self.data = data
