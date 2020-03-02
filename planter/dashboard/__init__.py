import os
from flask_bootstrap import Bootstrap
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
print(template_dir)
template_dir = os.path.join(template_dir, 'planter')
print(template_dir)
template_dir = os.path.join(template_dir, 'dashboard')
print(template_dir)
template_dir = os.path.join(template_dir, 'static')
template_dir = os.path.join(template_dir, 'templates')

dashboard = Flask(__name__, template_folder=template_dir)
dashboard.config.from_object(Config)
db = SQLAlchemy(dashboard)
bootstrap = Bootstrap(dashboard)

from dashboard import routes, models