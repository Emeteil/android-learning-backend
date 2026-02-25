from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
import secrets
import yaml, os
import logging

with open("settings.yml", "r", encoding="utf-8") as f:
    settings = yaml.load(f, Loader=yaml.FullLoader)

if settings['load_dotenv']:
    load_dotenv()

for env in settings['environment_variables']:
    settings[env] = os.environ.get(env)

app = FastAPI(
    debug=settings['debug']
)

if "cors" in settings:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings["cors"].get("allow_origins", ["*"]),
        allow_credentials=settings["cors"].get("allow_credentials", True),
        allow_methods=settings["cors"].get("allow_methods", ["*"]),
        allow_headers=settings["cors"].get("allow_headers", ["*"]),
    )

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

secret_key = settings.get("secret_key", secrets.token_urlsafe(32))

log_dir = settings["logging"]["log_dir"]
os.makedirs(log_dir, exist_ok=True)
log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
formatter = logging.Formatter(log_format)
log_level = logging.INFO if not settings["debug"] else logging.DEBUG
log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_filepath = os.path.join(log_dir, log_filename)

logger = logging.getLogger("fastapi")
logger.setLevel(log_level)
file_handler = logging.FileHandler(log_filepath)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(log_level)
uvicorn_file_handler = logging.FileHandler(log_filepath)
uvicorn_file_handler.setFormatter(formatter)
uvicorn_logger.addHandler(uvicorn_file_handler)