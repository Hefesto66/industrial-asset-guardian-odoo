from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class IndustrialAssetAPI(http.Controller):

    @http.route('/iag/api/update_metrics', type='http', auth='public', methods=['POST'], csrf=False)
    def update_metrics(self, **kw):
        """
        Endpoint to receive IoT sensor data.
        Expected Payload:
        {
            "serial_number": "SN-...",
            "temperature": float,
            "vibration": float
        }
        """
        try:
            raw_data = request.httprequest.data
            _logger.info("IAG API: Received payload")
            data = json.loads(raw_data)
        except Exception as e:
            _logger.error(f"IAG API: JSON Parsing Failure: {e}")
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

        # Sudo search required for public access
        asset = request.env['iag.asset'].sudo().search([('serial_number', '=', serial)], limit=1)

        if not asset:
            _logger.warning(f"IAG API: Asset not found for serial {serial}")
            return request.make_response(
                json.dumps({'status': 'error', 'message': 'Asset not found'}),
                headers=[('Content-Type', 'application/json')]
            )

        try:
            vals = {}
            if 'temperature' in data:
                vals['current_temperature'] = data['temperature']
            if 'vibration' in data:
                vals['current_vibration'] = data['vibration']

            if vals:
                asset.write(vals)

            response = {
                'status': 'success',
                'new_health_score': asset.health_score,
                'new_status': asset.status
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error(f"IAG API: Update Error: {e}")
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )
