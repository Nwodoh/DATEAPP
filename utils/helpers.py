import random
import string
from datetime import datetime, timedelta, timezone, date

def generate_otp(length:int=6) -> str:
    digits = string.digits # 0123456789 in a string
    otp = ''.join(random.choice(digits) for _ in range(length))
    return otp

def assign_res(res_type:str='success') -> dict:
    if not res_type: raise Exception("Invalid Response Type")
    return {'status': res_type}

def set_time_from_now(mins:int=10) -> datetime:
    time_from_now = datetime.now(timezone.utc) + timedelta(minutes=10) # datetime.utcnow() deprecated
    return time_from_now

def set_err_args(err_args:tuple, default_args:tuple=('Unknown Error', 500)) -> tuple:
    err_message, err_code = default_args
    if len(err_args) > 0 and err_args[0]: err_message = err_args[0]
    if len(err_args) > 1 and err_args[1]: err_code = err_args[1]
    return (err_message, err_code)

def is_future_date(dt:datetime) -> bool:
    return dt > datetime.now(timezone.utc)

def fromIsoStr(date_str:str):
    if not date_str: raise Exception('Invalid Date String.', 403)
    return date.fromisoformat(date_str)