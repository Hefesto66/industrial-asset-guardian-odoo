from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class IndustrialAssetAPI(http.Controller):

    # I define this route with 'auth=public' to allow external IoT devices to push data without complex login flows.
    # I disable CSRF protection (csrf=False) because IoT devices cannot easily handle session tokens.
    # I use type='http' instead of 'json' to support raw JSON payloads, which are more standard for IoT.
    @http.route('/iag/api/update_metrics', type='http', auth='public', methods=['POST'], csrf=False)
    def update_metrics(self, **kw):
        """
        I accept a raw JSON payload in the following format:
        {
            "serial_number": "SN-12345",
            "temperature": 85.5,
            "vibration": 3.2
        }
        I rely on the serial_number to identify the asset.
        """
        try:
            # I read the raw data stream from the request.
            raw_data = request.httprequest.data
            _logger.info(f"IAG API: Received IoT Payload: {raw_data}")
            data = json.loads(raw_data)
        except Exception as e:
            _logger.error(f"IAG API: JSON Parsing Faulure: {e}")
            return request.make_response(
                json.dumps({'status': 'error', 'message': 'Invalid JSON format'}),
                headers=[('Content-Type', 'application/json')]
            )

        serial = data.get('serial_number')

        if not serial:
            return request.make_response(
                json.dumps({'status': 'error', 'message': 'Serial Number required'}),
                headers=[('Content-Type', 'application/json')]
            )

        # I search for the asset in the database using sudo() to bypass record rules,
        # ensuring the system can find the asset even if the public user has no read access.
        asset = request.env['iag.asset'].sudo().search([('serial_number', '=', serial)], limit=1)
        _logger.info(f"IAG API: Searching for Serial {serial} - Found: {asset}")

        if not asset:
            return request.make_response(
                json.dumps({'status': 'error', 'message': 'Asset not found'}),
                headers=[('Content-Type', 'application/json')]
            )

        # I prepare the values to update. I only update what was provided in the JSON.
        try:
            vals = {}
            if 'temperature' in data:
                vals['current_temperature'] = data['temperature']
            if 'vibration' in data:
                vals['current_vibration'] = data['vibration']

            # I write the new values to the asset record. This will trigger the automation in models/asset.py.
            asset.write(vals)

            # I build the success response including the new calculated health state.
            response = {
                'status': 'success',
                'new_health_score': asset.health_score,
                'new_status': asset.status
            }
            _logger.info(f"IAG API: Update Successful: {response}")
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error(f"IAG API: Logic Error: {e}")
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )
