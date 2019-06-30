import ipaddress
import os

from flask import Flask
from flask import request
from flask import jsonify

import geoip2.database
import geoip2.errors

app = Flask(__name__)

reader = geoip2.database.Reader(f"{os.environ.get('APP_ROOT', './')}databases/GeoLite2-City.mmdb")


@app.route('/', methods=['GET'])
def ip_echo():
    try:
        response = reader.city(request.remote_addr)
        return jsonify(geoip_response_to_dict(response)), 200
    except geoip2.errors.AddressNotFoundError:
        return jsonify({'error': 'IP not in database'}), 404


@app.route('/api/geoip', methods=['GET'])
def ip_reply():
    try:
        ip = request.args.get('ip')
        ipaddress.ip_address(ip)
        response = reader.city(ip)
        return jsonify(geoip_response_to_dict(response)), 200
    except ValueError:
        return jsonify({'error': f"{ip} is not a valid IP address"}), 400
    except geoip2.errors.AddressNotFoundError:
        return jsonify({'error': 'IP not in database'}), 404


@app.route('/status', methods=['GET'])
def status_check():
    return jsonify({'status': 'healthy'}), 200


def geoip_response_to_dict(response):
    city = response.city
    country = response.country
    return {
        "city": {
            "name": city.name,
            "postal_code": response.postal.code,
            "subdivision": {
                "name": response.subdivisions.most_specific.name,
                "code": response.subdivisions.most_specific.iso_code
            }
        },
        "country": {
            "country_code": country.iso_code,
            "country_name": country.name
        },
        "geography": {
            "latitude": response.location.latitude,
            "longitude": response.location.longitude
        }
    }


if __name__ == '__main__':
    app.run(host=os.environ.get('BIND_ADDRESS', '0.0.0.0'),
            threaded=True)
