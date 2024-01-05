from loguru import logger
import sys

logger.bind(context="server")
# scheduler_logger = logger.bind(context="scheduler")

logger.add(
    "server.log",
    rotation="7 days",
    level="INFO",
    backtrace=True,
    diagnose=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level}</level> | "
    "<cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
)
# logger.add(
#     sys.stderr,
#     level="INFO",
#     backtrace=True,
#     diagnose=True,
#     format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
#     "<level>{level}</level> | "
#     "<cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
# )
