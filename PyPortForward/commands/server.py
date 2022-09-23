from flask import Flask, request
from flask_cors import CORS
import json
import logging

import PyPortForward as ppf

app = Flask(__name__)
CORS(app)

def server(host, port, debug):
    """
    PortForward Manager start point
    """
    app.run(host=host, port=port, debug=debug)