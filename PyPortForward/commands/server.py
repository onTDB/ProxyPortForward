from flask import Flask, request
from flask_cors import CORS
import json
import logging

import PyPortForward as ppf

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return "PyPortForward Server\nHello World!"


def server(host, port, debug):
    """
    PortForward Manager start point
    """
    app.run(host=host, port=port, debug=debug)