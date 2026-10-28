"""
Package: service
Package for the Account Service
"""
from flask import Flask
from flask_talisman import Talisman
from flask_cors import CORS

app = Flask(__name__)

############################################################
# Security Headers via Talisman
############################################################
talisman = Talisman(app)

############################################################
# CORS Policies
############################################################
CORS(app)

from service import routes, models  # noqa: F401, E402
