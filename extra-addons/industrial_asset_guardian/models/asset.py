from odoo import models, fields, api


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

    # --- INTELLIGENCE FIELDS ---

    # I define these fields to simulate real-time sensor readings that will eventually come from IoT devices.
    current_temperature = fields.Float(string='Temperature (°C)', default=25.0, tracking=True)
    current_vibration = fields.Float(string='Vibration (mm/s)', default=0.0, tracking=True)

    # I enforce these technical limits to detect anomalies. Ideally, I would make them configurable per asset type later.
    max_temperature = fields.Float(string='Max Temp Allowed', default=90.0)
    max_vibration = fields.Float(string='Max Vib Allowed', default=5.0)

    # I compute this field automatically to provide a synthesized health metric (0-100%).
    # I store it in the database (store=True) to allow me to use it in graphs and filters.
    def _compute_health_score(self):
        pass  # Placeholder for the method below

    health_score = fields.Integer(
        string='Health Score',
        compute='_compute_health_score',
        store=True,
        help="Calculated based on temperature and vibration stress."
    )

    @api.depends('current_temperature', 'current_vibration', 'max_temperature', 'max_vibration')
    def _compute_health_score(self):
        """
        I calculate the health score by applying penalties based on how much the metrics exceed their limits.
        """
        for record in self:
            score = 100  # I start with a perfect score.

            # I apply tiered penalties for Temperature.
            if record.current_temperature > (record.max_temperature * 1.2):
                score -= 80  # I deduct a massive amount if it exceeds the limit by 20%.
            elif record.current_temperature > record.max_temperature:
                score -= 50  # I deduct half the health if it simply exceeds the limit.
            elif record.current_temperature > (record.max_temperature * 0.8):
                score -= 10  # I apply a small warning penalty if it gets close (80%) to the limit.

            # I apply similar tiered penalties for Vibration.
            if record.current_vibration > (record.max_vibration * 1.5):
                score -= 80
            elif record.current_vibration > record.max_vibration:
                score -= 50
            elif record.current_vibration > (record.max_vibration * 0.5):
                score -= 20

            # I ensure the score never drops below zero.
            record.health_score = max(0, score)

    # --- BUSINESS LOGIC AND AUTOMATION ---

    @api.onchange('current_temperature', 'current_vibration', 'health_score')
    def _onchange_health_check(self):
        """
        I provide immediate visual feedback in the UI when the user manually changes values.
        If the health score drops to critical levels, I switch the status to Maintenance immediately.
        """
        if self.health_score <= 50 and self.status == 'operational':
            self.status = 'maintenance'
            return {'warning': {
                'title': "Critical Warning",
                'message': f"Health Score dropped to {self.health_score}%! Status changed to Maintenance."
            }}

    def write(self, vals):
        """
        I override the write method to ensure my automation rules apply regardless of how the data is updated
        (e.g., via the API, bulk imports, or the backend).
        """
        # 1. I allow Odoo to save the new values first to ensure consistency.
        res = super(IndustrialAsset, self).write(vals)

        # 2. I verify the business logic AFTER the save has persisted.
        for record in self:
            if record.health_score <= 50 and record.status == 'operational':
                record.status = 'maintenance'
                # I automatically trigger a maintenance request to the maintenance team.
                record._create_maintenance_request()

        return res

    def _create_maintenance_request(self):
        """
        I create an official Odoo Maintenance Request to alert the team.
        I also check for existing open requests to avoid spamming the system with duplicates.
        """
        # I ensure the maintenance module is actually installed before trying to access it.
        if 'maintenance.request' not in self.env:
            return

        MaintenanceRequest = self.env['maintenance.request']

        # 1. I check if there is arguably already an ACTIVE request for this asset description.
        # I filter by the unarchived and unfinished stages.
        existing_request = MaintenanceRequest.search([
            ('description', 'ilike', self.serial_number),
            ('archive', '=', False),
            ('stage_id.done', '=', False)
        ], limit=1)

        if not existing_request:
            # 2. I create the critical maintenance ticket.
            force_title = f'CRITICAL: {self.name} - Overheating/Vibration'
            MaintenanceRequest.create({
                'name': force_title,
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

                    Please inspect immediately and apply LOTO procedures.
                """
            })
            # I post a notification in the asset's chatter to log that I took this action.
            self.message_post(body="🚨 Maintenance Request created automatically due to critical health score.")