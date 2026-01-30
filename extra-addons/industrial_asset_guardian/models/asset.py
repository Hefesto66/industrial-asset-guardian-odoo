from odoo import models, fields, api, _


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

    health_score = fields.Integer(
        string='Health Score',
        compute='_compute_health_score',
        store=True,
        help="Calculated based on temperature and vibration stress."
    )

    @api.depends('current_temperature', 'current_vibration', 'max_temperature', 'max_vibration')
    def _compute_health_score(self):
        """
        Calculate asset health score (0-100) based on operational limits.
        Penalties increase as metrics exceed safety thresholds.
        """
        for record in self:
            score = 100

            # Temperature penalties
            if record.current_temperature > (record.max_temperature * 1.2):
                score -= 80
            elif record.current_temperature > record.max_temperature:
                score -= 50
            elif record.current_temperature > (record.max_temperature * 0.8):
                score -= 10

            # Vibration penalties
            if record.current_vibration > (record.max_vibration * 1.5):
                score -= 80
            elif record.current_vibration > record.max_vibration:
                score -= 50
            elif record.current_vibration > (record.max_vibration * 0.5):
                score -= 20

            record.health_score = max(0, score)

    @api.onchange('current_temperature', 'current_vibration', 'health_score')
    def _onchange_health_check(self):
        if self.health_score <= 50 and self.status == 'operational':
            self.status = 'maintenance'
            return {'warning': {
                'title': _("Critical Warning"),
                'message': _("Health Score dropped to %s%%! Status changed to Maintenance.") % self.health_score
            }}

    def write(self, vals):
        res = super(IndustrialAsset, self).write(vals)

        # Post-write check: trigger maintenance if health critical
        for record in self:
            if record.health_score <= 50 and record.status == 'operational':
                record.status = 'maintenance'
                record._create_maintenance_request()

        return res

    def _create_maintenance_request(self):
        """
        Generates a maintenance request if one doesn't already exist for this issue.
        """
        if 'maintenance.request' not in self.env:
            return

        MaintenanceRequest = self.env['maintenance.request']

        # Prevent duplicate requests for the same asset
        existing_request = MaintenanceRequest.search([
            ('description', 'ilike', self.serial_number),
            ('archive', '=', False),
            ('stage_id.done', '=', False)
        ], limit=1)

        if not existing_request:
            MaintenanceRequest.create({
                'name': _('CRITICAL: %s - Overheating/Vibration') % self.name,
                'request_date': fields.Date.today(),
                'maintenance_type': 'corrective',
                'priority': '3',
                'description': f"""
                    AUTOMATED ALERT IAG SYSTEM
                    --------------------------
                    Asset: {self.name}
                    Serial: {self.serial_number}

                    Current Metrics:
                    - Temperature: {self.current_temperature}°C (Max: {self.max_temperature})
                    - Vibration: {self.current_vibration} mm/s (Max: {self.max_vibration})

                    Please inspect immediately.
                """
            })
            self.message_post(body=_("🚨 Maintenance Request created automatically due to critical health score."))
