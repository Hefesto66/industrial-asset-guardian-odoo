from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestIndustrialAssetLogic(TransactionCase):

    def setUp(self):
        super(TestIndustrialAssetLogic, self).setUp()
        # I create a test asset to be used in all test cases.
        self.asset = self.env['iag.asset'].create({
            'name': 'Test Turbine',
            'serial_number': 'TEST-001',
            'max_temperature': 100.0,
            'max_vibration': 10.0,
            'current_temperature': 50.0, # Safe value
            'current_vibration': 0.0,    # Safe value
            'status': 'operational'
        })

    def test_health_score_calculation_safe(self):
        """ I verify that safe metrics result in a 100% health score. """
        self.asset._compute_health_score()
        self.assertEqual(self.asset.health_score, 100, "Health Score should be 100 for safe metrics.")

    def test_health_score_calculation_critical_temp(self):
        """ I verify that critical temperature drops the score significantly. """
        # Temperature 130 is 30% above 100, so it hits the >20% penalty tier (-80 points)
        self.asset.write({'current_temperature': 130.0})
        self.asset._compute_health_score()
        # Initial 100 - 80 = 20
        self.assertEqual(self.asset.health_score, 20, "Health Score should drop to 20 for critical overheating.")

    def test_maintenance_trigger(self):
        """ I verify that low health score automatically triggers maintenance status. """
        # I force a write that should trigger the automation
        self.asset.write({'current_temperature': 130.0}) 
        
        # The write method override should have detected the new score (20) and changed status
        self.assertEqual(self.asset.status, 'maintenance', "Status should automatically change to 'maintenance'.")

    def test_maintenance_request_creation(self):
        """ I verify that a Maintenance Request is created when status flips. """
        # I ensure 'maintenance' module is installed for this test
        if 'maintenance.request' not in self.env:
            print("Maintenance module not installed, skipping test.")
            return

        # Trigger critical failure
        self.asset.write({'current_temperature': 130.0})

        # Search for the created request
        request = self.env['maintenance.request'].search([
            ('description', 'ilike', 'TEST-001')
        ], limit=1)

        self.assertTrue(request, "A Maintenance Request should have been created.")
        self.assertIn("CRITICAL", request.name, "Request title should indicate criticality.")
