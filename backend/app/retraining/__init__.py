from flask import Blueprint

retraining_bp = Blueprint('retraining', __name__)

from . import routes