import os

from flask import Flask
from flask import g
from flask import request
from flask import Response
from flask import jsonify

import geoip2.database
import geoip2.errors
import maxminddb.errors

from reader import GeoIPReader

app = Flask(__name__)


def process_request(ip):
    try:
        reader = get_database_reader()
        response = reader.handle_ip_query(ip)
        return jsonify(response), 200
    except ValueError:
        return jsonify({'error': f"{ip} is not a valid IP address"}), 400
    except geoip2.errors.AddressNotFoundError:
        return jsonify({'error': 'IP not in database'}), 404
    except maxminddb.errors.InvalidDatabaseError:
        response = Response(jsonify({'error': 'Database upgrade in progress, please retry'}), 429)
        response.headers['Retry-After'] = 5
        return response


@app.route('/', methods=['GET'])
def ip_echo():
    return process_request(request.remote_addr)


@app.route('/api/geoip', methods=['GET'])
def ip_reply():
    return process_request(request.args.get('ip', ""))


@app.route('/status', methods=['GET'])
def status_check():
    return jsonify({'status': 'healthy'}), 200


@app.teardown_appcontext
def close_database(context):
    reader = g.pop('geoip_reader', None)

    if reader is not None:
        reader.cursor.close()


def get_database_reader():
    if not hasattr(g, 'geoip_reader'):
        g.geoip_reader = GeoIPReader(f"{os.environ.get('APP_ROOT', './')}databases/GeoLite2-City.mmdb")
    return g.geoip_reader


if __name__ == '__main__':
    app.run(host=os.environ.get('BIND_ADDRESS', '0.0.0.0'))
