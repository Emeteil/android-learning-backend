from datetime import datetime
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
)

if "json" in dir(app) and hasattr(app.json, 'ensure_ascii'):
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    app.json.compact = False

app.config["JSON_AS_ASCII"] = False
app.config["JSON_SORT_KEYS"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.config['SECRET_KEY'] = settings.get("flask_secret", secrets.token_urlsafe(32))


log_dir = settings["logging"]["log_dir"]
os.makedirs(log_dir, exist_ok=True)
log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
formatter = logging.Formatter(log_format)
log_level = logging.INFO if not settings["debug"] else logging.DEBUG
log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_filepath = os.path.join(log_dir, log_filename)
app.logger.setLevel(log_level)
file_handler = logging.FileHandler(log_filepath)
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(logging.Formatter("%(message)s"))
# app.logger.addHandler(console_handler)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(log_level)
werkzeug_file_handler = logging.FileHandler(log_filepath)
werkzeug_file_handler.setFormatter(formatter)
werkzeug_logger.addHandler(werkzeug_file_handler)
werkzeug_console_handler = logging.StreamHandler()
werkzeug_console_handler.setFormatter(logging.Formatter("%(message)s"))
werkzeug_logger.addHandler(werkzeug_console_handler)
app.logger.propagate = False
werkzeug_logger.propagate = False