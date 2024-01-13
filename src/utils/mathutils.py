def truncate_to_4_decimal(number: float) -> float:
    multiplier = 10**4
    return int(number * multiplier) / multiplier

def truncate_to_2_decimal(number: float) -> float:
    multiplier = 10**2
    return int(number * multiplier) / multiplier

def convert_amout_to_string(amount: float):
    formatted_number = "{:.2f}".format(amount)
    return formatted_number


def convert_qty_to_string(qty: float):
    formatted_number = "{:.4f}".format(qty)
    return formatted_number


def format_qty(qty: float, to_string: bool = False):
    if to_string:
        return convert_qty_to_string(qty)
    return truncate_to_4_decimal(qty)


def format_amt(amt: float, to_string: bool = False):
    amt = round(amt, 2)
    if to_string:
        return convert_amout_to_string(amt)
    return amt


