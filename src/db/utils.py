from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime
import re


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


def get_table_name(raw_table_name):
    snake_case_string = re.sub(r"(?<!^)(?=[A-Z])", "_", raw_table_name).lower()
    if snake_case_string[-1] == "s":
        return snake_case_string + "es"
    else:
        return snake_case_string + "s"
