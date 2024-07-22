from sqlalchemy.exc import SQLAlchemyError

from exceptions.custom_exceptions import CustomException
from exceptions.exception_messages import INVALID_DATABASE_QUERY_EXCEPTION


def raise_invalid_db_query_error(err: SQLAlchemyError):
    import sys
    import traceback

    # raise CustomException(*INVALID_DB_QUERY_EXCEPTION_FOR_USER)

    ex_type, ex_value, ex_traceback = sys.exc_info()

    # Extract unformatter stack traces as tuples
    trace_back = traceback.extract_tb(ex_traceback)
    # Format stacktrace
    stack_trace = list()
    for trace in trace_back:
        stack_trace.append(
            f"File: {trace[0]}, Line: {trace[1]}, FuncName: {trace[2]}, Message: {trace[3]}"
        )

    custom_message = list(INVALID_DATABASE_QUERY_EXCEPTION)
    custom_message[2] = custom_message[2].format(ex_type, ex_value, stack_trace)
    raise CustomException(*custom_message)
