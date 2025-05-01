from flask import Blueprint

authentications_bp = Blueprint('authentications_bp', __name__)

from . import routes