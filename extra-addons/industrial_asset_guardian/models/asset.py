from odoo import models, fields

class IndustrialAsset(models.Model):
    _name = 'iag.asset'
    _description = 'Industrial Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    serial_number = fields.Char(string='Serial Number', copy=False)

    asset_type = fields.Selection([
        ('motor', 'Electric Motor'),
        ('pump', 'Hydraulic Pump'),
        ('sensor', 'IoT Sensor'),
        ('conveyor', 'Conveyor Belt')
    ], string='Asset Type', required=True, default='motor')

    status = fields.Selection([
        ('draft', 'Draft'),
        ('operational', 'Operational'),
        ('maintenance', 'In Maintenance'),
        ('retired', 'Retired')
    ], string='Status', default='draft', tracking=True)

    installation_date = fields.Date(string='Installation Date')
    description = fields.Text(string='Technical Specifications')

    # IoT Metrics
    current_temperature = fields.Float(string='Temperature (°C)', default=25.0, tracking=True)
    current_vibration = fields.Float(string='Vibration (mm/s)', default=0.0, tracking=True)

    # Thresholds
    max_temperature = fields.Float(string='Max Temp Allowed', default=90.0)
    max_vibration = fields.Float(string='Max Vib Allowed', default=5.0)

    health_score = fields.Integer(string='Health Score', store=True, help="Calculated based on temperature and vibration stress.")
