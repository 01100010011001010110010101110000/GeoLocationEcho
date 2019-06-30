import geoip2.database
import geoip2.errors
import geoip2.models
import maxminddb.errors


class GeoIPReader():
    cursor = None
    databsae_path = ''

    def __init__(self, database_path):
        """
        Intializes the class' database connection
        :param database_path: Path to a MaxMind cities binary database
        """
        self.cursor = geoip2.database.Reader(database_path)
        self.database_path = database_path

    def handle_ip_query(self, ip: str) -> dict:
        """
        Queries the MaxMind database for an IP address

        In the event of an `InvalidDatabaseError`, we recreate the database connection
        :param ip: IP Address to
        :return: GeoIP database attributes parsed into a dict
        """
        try:
            database_reader = self.get_database_reader()
            response = database_reader.city(ip)
            return self.geoip_response_to_dict(response)
        except maxminddb.errors.InvalidDatabaseError as e:
            self.refresh_reader()
            raise e

    @staticmethod
    def geoip_response_to_dict(response: geoip2.models.City) -> dict:
        """

        :param response: A City response from a GeoIP2 database.city(`ip`) read call
        :return: The attributes of that model parsed into a dictionary
        """
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

    def get_database_reader(self):
        if not self.cursor:
            self.cursor = geoip2.database.Reader(self.database_path)
        return self.cursor

    def refresh_reader(self):
        if self.cursor is not None:
            self.cursor.close()
        self.get_database_reader()

    def __del__(self):
        """
        Close the database connection on deconstruction
        """
        if self.cursor is not None:
            self.cursor.close()
