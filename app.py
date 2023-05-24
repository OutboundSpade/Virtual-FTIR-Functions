# Flask server
#   https://flask.palletsprojects.com/en/2.2.x/
#   python3 flask_api.py

import json

from flask import Flask, request
from flask_cors import CORS
from functions import (
    __generate_spectrum,
    __param_check,
    __process_background,
    __process_spectrum,
)

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def ftir():
    return "<h1 style='color:blue'>Raston Lab FTIR API</h1>"


@app.route("/spectrum", methods=["POST"])
def spectrum():
    # put incoming JSON into a dictionary
    params = json.loads(request.data)

    # verify user input is valid
    if not __param_check(params):
        return {
            "success": False,
            "text": "Parameter check failed",
        }

    # perform:
    #   --> transmission spectrum of gas sample (calc_spectrum)
    spectrum, error, message = __generate_spectrum(params)
    if error:
        return {
            "success": False,
            "text": message,
        }

    # perform:
    #   --> blackbody spectrum of source (sPlanck)
    #   --> transmission spectrum of beamsplitter and cell windows
    #   --> detector response spectrum
    processed_spectrum = __process_spectrum(params, spectrum, True)

    # https://radis.readthedocs.io/en/latest/source/radis.spectrum.spectrum.html#radis.spectrum.spectrum.Spectrum.get
    x_value, y_value = processed_spectrum.get("transmittance_noslit")

    # convert dictionary values to strings and return as JSON
    return {
        "success": True,
        "x": list(x_value),
        "y": list(map(str, y_value)),
    }


@app.route("/background", methods=["POST"])
def background():
    # put incoming JSON into a dictionary
    data = json.loads(request.data)

    # verify user input is valid
    if not __param_check(data):
        return {
            "success": False,
            "text": "Parameter check failed",
        }

    # perform:
    #   --> transmission spectrum of gas sample (calc_spectrum)
    spectrum, error, message = __generate_spectrum(data)
    if error:
        return {
            "success": False,
            "text": message,
        }

    # perform:
    #   --> set all y-values to one
    background_spectrum = __process_background(spectrum)

    # perform:
    #   --> blackbody spectrum of source (sPlanck)
    #   --> transmission spectrum of beamsplitter and cell windows
    #   --> detector response spectrum
    processed_spectrum = __process_spectrum(data, background_spectrum, True)

    # https://radis.readthedocs.io/en/latest/source/radis.spectrum.spectrum.html#radis.spectrum.spectrum.Spectrum.get
    x_value, y_value = processed_spectrum.get("transmittance_noslit")

    # convert dictionary values to strings and return as JSON
    return {
        "success": True,
        "x": list(x_value),
        "y": list(map(str, y_value)),
    }

@app.route("/find_peaks", methods=["POST"])
def find_peaks():
    data = json.loads(request.data)

    print("Got the request!")

    return {
        "success": True,
    }

# set debug to false in production environment
if __name__ == "__main__":
    app.run(host="0.0.0.0")
