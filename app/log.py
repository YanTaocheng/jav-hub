import logging
import logging.handlers
import os


def setup_logger():
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(name)s - %(message)s')
    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(os.getenv('LOG_LEVEL'))

    if not os.path.exists("../config"):
        os.makedirs("../config")

    file_handler = logging.handlers.RotatingFileHandler(filename='../config/jav-hub.log', maxBytes=5000000, backupCount=2, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(os.getenv('LOG_LEVEL'))
    # config log
    logging.basicConfig(handlers=[console_handler, file_handler], level=logging.DEBUG)

    # 获取 httpx 的日志记录器
    httpx_logger = logging.getLogger("httpx")
    # 将 httpx 的日志级别设置为 WARNING
    httpx_logger.setLevel(logging.WARNING)

    # uvicorn log
    logging.getLogger("uvicorn.access").addHandler(console_handler)
    logging.getLogger("uvicorn.error").addHandler(console_handler)
    logging.getLogger("uvicorn.asgi").addHandler(console_handler)
    # logging.getLogger("uvicorn.access").addHandler(file_handler)
    logging.getLogger("uvicorn.error").addHandler(file_handler)
    # logging.getLogger("uvicorn.asgi").addHandler(file_handler)
    
    # remove uvicorn default handler
    # logging.getLogger("uvicorn").removeHandler(logging.getLogger("uvicorn").handlers[0])
    logging.getLogger("uvicorn.error").removeHandler(logging.getLogger("uvicorn.error").handlers[0])
    logging.getLogger("uvicorn.access").removeHandler(logging.getLogger("uvicorn.access").handlers[0])
    logging.getLogger("uvicorn.asgi").removeHandler(logging.getLogger("uvicorn.asgi").handlers[0])
    
    logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
    # # sql alchemy
    # logging.getLogger("sqlalchemy.engine").setLevel(os.getenv('LOG_LEVEL_SQLALCHEMY_ENGINE'))
    # logging.getLogger("sqlalchemy.pool").setLevel(os.getenv('LOG_LEVEL_SQLALCHEMY_POOL'))
