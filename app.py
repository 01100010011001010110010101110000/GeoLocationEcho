import os

from flask import Flask
from flask import g
from flask import request
from flask import Response
from flask import jsonify

import geoip2.database
import geoip2.errors
import maxminddb.errors

app = Flask(__name__)


@app.route('/', methods=['GET'])
def ip_echo():
    return handle_ip_query(request.remote_addr)


@app.route('/api/geoip', methods=['GET'])
def ip_reply():
    return handle_ip_query(request.args.get('ip', ""))


@app.route('/status', methods=['GET'])
def status_check():
    return jsonify({'status': 'healthy'}), 200


def handle_ip_query(ip):
    try:
        database_reader = get_database_reader()
        response = database_reader.city(ip)
        return jsonify(geoip_response_to_dict(response)), 200
    except ValueError:
        return jsonify({'error': f"{ip} is not a valid IP address"}), 400
    except geoip2.errors.AddressNotFoundError:
        return jsonify({'error': 'IP not in database'}), 404
    except maxminddb.errors.InvalidDatabaseError:
        refresh_reader()
        response = Response(jsonify({'error': 'Database upgrade in progress, please retry'}), 429)
        response.headers['Retry-After'] = 5
        return response


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


@app.teardown_appcontext
def close_database(context):
    db = g.pop('geoip_reader', None)

    if db is not None:
        db.close()


def get_database_reader():
    if not hasattr(g, 'geoip_reader'):
        g.geoip_reader = geoip2.database.Reader(f"{os.environ.get('APP_ROOT', './')}databases/GeoLite2-City.mmdb")
    return g.geoip_reader


def refresh_reader():
    db = g.pop('geoip_reader', None)

    if db is not None:
        db.close()
    get_database_reader()


if __name__ == '__main__':
    app.run(host=os.environ.get('BIND_ADDRESS', '0.0.0.0'))
