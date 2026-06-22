from flask import Blueprint

api_generator_bp = Blueprint('api_generator', __name__)

from . import routes