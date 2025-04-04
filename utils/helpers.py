import math
import random
import string
from datetime import datetime, timedelta, timezone, date
import time


# contains different function used for helpers within other functions through out the application.


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def generate_chat_id(first_user:str, second_user:str):
    return str(time.time()) + '-' + get_chat_room_key(first_user, second_user)

def generate_otp(length:int=6) -> str:
    digits = string.digits # 0123456789 in a string
    otp = ''.join(random.choice(digits) for _ in range(length))
    return otp

def assign_res(res_type:str='success') -> dict:
    if not res_type: raise Exception("Invalid Response Type")
    return {'status': res_type}

def set_time_from_now(mins:int=10) -> datetime:
    time_from_now = datetime.now(timezone.utc) + timedelta(minutes=mins) # datetime.utcnow() deprecated
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

def get_chat_room_key(user_id:str, other_user_id:str):
    return "".join(sorted(user_id + other_user_id))
    
def add_random_decimal(numbers):
    randomized_numbers = []
    for num in numbers:
        if isinstance(num, int):
            # Generate a random five-digit decimal
            random_decimal = random.randint(10000, 99999)
            # Combine the integer and the random decimal
            new_number = float(f"{num}.0{random_decimal}")
        elif isinstance(num, float):
            # Extract the integer part
            integer_part, decimal_part = str(num).split('.')
            # Get the first digit of the decimal part
            first_decimal_digit = int(decimal_part[0])
            # Generate a new random five-digit decimal
            random_decimal = random.randint(10000, 99999)
            # Combine them to form the new float
            new_number = float(f"{integer_part}.{first_decimal_digit}{random_decimal}")
        else:
            raise ValueError("List elements must be either int or float")
        randomized_numbers.append(new_number)
    return randomized_numbers

# numbers = [6, 3.14159, 42, 7.89]
# randomized_numbers = add_random_decimal(numbers)
# print(randomized_numbers)
# print(haversine(6.45407, 3.39467,  40.730610, -73.935242))