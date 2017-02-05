#!/usr/bin/python3

from flask import Flask, request, jsonify, send_file
from naniologger import logger
# import bthandler

app = Flask("naniolightshow")


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

@app.route('/')
def send_template():
    return send_file('index.html')

@app.route('/hsi', methods=['POST'])
def set_hsi():
    color_data = request.get_json()
    logger.info("Received request to set HSI")
    if 'hue' and 'saturation' and 'intensity' in color_data:
        hue = int(color_data['hue'])
        sat = float(color_data['saturation'])
        intensity = float(color_data['intensity'])

        hue = clamp(hue, 0, 360)
        sat = clamp(sat, 0, 1)
        intensity = clamp(intensity, 0, 1)

        logger.info("Setting hue: %s, sat: %s, int: %s", hue, sat, intensity)

        # TODO: write colors to bluetooth

        # send response
        return jsonify({"result": "success", "message": "Setting HSI", "data": {"hue": hue, "saturation": sat, "intensity": intensity}}), 200
    else:
        logger.info("Request does not contain correct parameters")
        return jsonify({"result": "error", "message": "Please specify hue, saturation and intensity"})


@app.route('/rgb', methods=['POST'])
def set_rgb():
    color_data = request.get_json()
    logger.info("Received request to set RGB")
    if 'red' and 'green' and 'blue' in color_data:
        r = int(color_data['red'])
        g = float(color_data['green'])
        b = float(color_data['blue'])

        logger.info("Setting red: %s, green: %s, blue: %s", r, g, b)
        # TODO: write colors to bluetooth

        # send response
        return jsonify({"result": "success", "message": "Setting RGB", "data": {"red": r, "green": g, "blue": b}}), 200
    else:
        logger.info("Request does not contain correct parameters")
        return jsonify({"result": "error", "message": "Please specify red, green and blue"})


@app.route('/pulse/<period_ms>', methods=['GET'])
def pulse(period_ms):
    period_ms = int(period_ms)

    # TODO: write pulse to bluetooth

    # clamp above epileptic frequency (~ 8 Hz)
    if period_ms < 125:
        period_ms = 125

    return jsonify({"result": "success", "message": "Pulsing LEDs", "data": {"period_ms": period_ms, "frequency": '{:.2f}'.format(1000 / period_ms)}})


@app.route('/blink/<period_ms>', methods=['GET'])
def blink(period_ms):
    period_ms = int(period_ms)

    # TODO: write blink to bluetooth

    # clamp above epileptic frequency (~ 8 Hz)
    if period_ms < 125:
        period_ms = 125

    return jsonify({"result": "success", "message": "Blinking LEDs", "data": {"period_ms": period_ms, "frequency": '{:.2f}'.format(1000 / period_ms)}})


@app.route('/cycle/<period_ms>', methods=['GET'])
def cycle(period_ms):
    period_ms = int(period_ms)

    # TODO: write cycle to bluetooth

    # clamp above epileptic frequency (~ 8 Hz)
    if period_ms < 125:
        period_ms = 125

    return jsonify({"result": "success", "message": "Cycling LEDs", "data": {"period_ms": period_ms, "frequency": '{:.2f}'.format(1 / period_ms)}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
