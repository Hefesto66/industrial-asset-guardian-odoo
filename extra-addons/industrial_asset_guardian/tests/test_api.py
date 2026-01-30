from odoo.tests.common import HttpCase
import json


class TestIndustrialAssetAPI(HttpCase):

    def setUp(self):
        super(TestIndustrialAssetAPI, self).setUp()
        # I create a test asset to receive API data.
        self.asset = self.env['iag.asset'].create({
            'name': 'API Test Turbine',
            'serial_number': 'API-TEST-001',
            'current_temperature': 50.0,
            'status': 'operational'
        })

    def test_api_update_metrics_success(self):
        """ T05: I verify that the API updates the database correctly (Status 200). """
        payload = {
            "serial_number": "API-TEST-001",
            "temperature": 85.0,
            "vibration": 2.5
        }

        # I force sending JSON data as a raw string because my controller reads request.httprequest.data
        response = self.url_open(
            '/iag/api/update_metrics',
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200, "API should return 200 OK.")

        # I invalidate the cache to ensure I read the latest value from the DB
        self.asset.invalidate_model(['current_temperature', 'current_vibration'])
        self.assertEqual(self.asset.current_temperature, 85.0, "Temperature should be updated via API.")

    def test_api_anti_spam_maintenance(self):
        """ T06: I verify that multiple critical API calls result in only ONE maintenance request. """
        # I ensure maintenance module is installed
        if 'maintenance.request' not in self.env:
            return

        payload = {
            "serial_number": "API-TEST-001",
            "temperature": 150.0,  # Critical!
            "vibration": 20.0     # Critical!
        }

        # I spam the API 5 times
        for _ in range(5):
            self.url_open(
                '/iag/api/update_metrics',
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )

        # I check how many requests were created
        requests_count = self.env['maintenance.request'].search_count([
            ('description', 'ilike', 'API-TEST-001')
        ])

        self.assertEqual(requests_count, 1, "There should be exactly ONE maintenance request despite multiple API calls.")
