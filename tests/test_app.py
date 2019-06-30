from unittest import TestCase

import geoip2.errors

from reader import GeoIPReader


class TestGeoLocationEcho(TestCase):
    reader = GeoIPReader('GeoLite2-City.mmdb')

    def test_handle_ip_query_known_good(self):
        response = self.reader.handle_ip_query('8.8.8.8')
        self.assertIsNotNone(response)

    def test_handle_ip_query_ipv6(self):
        response = self.reader.handle_ip_query('2001:4860:4860::8888')
        self.assertIsNotNone(response)

    def test_handle_ip_query_empty(self):
        with self.assertRaises(TypeError):
            self.reader.handle_ip_query(None)
        with self.assertRaises(ValueError):
            self.reader.handle_ip_query('')

    def test_handle_ip_query_malformed(self):
        with self.assertRaises(ValueError):
            self.reader.handle_ip_query('dabkhusba')

    def test_handle_ip_query_rfc1918(self):
        with self.assertRaises(geoip2.errors.AddressNotFoundError):
            self.reader.handle_ip_query('10.0.0.1')
