from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError
from odoo.tests import tagged


@tagged('security')
class TestIndustrialAssetSecurity(TransactionCase):

    def setUp(self):
        super(TestIndustrialAssetSecurity, self).setUp()
        # I create a standard user without any specific IAG groups (assuming default is restrictive).
        self.user_bob = self.env['res.users'].create({
            'name': 'Bob The Intruder',
            'login': 'bob_intruder',
            'email': 'bob@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]  # Internal User only
        })

        self.asset = self.env['iag.asset'].create({
            'name': 'Secure Turbine',
            'serial_number': 'SEC-001',
        })

    def test_read_access_denied(self):
        """ T07: I verify that a user without proper groups simply cannot read the asset data. """
        # I switch to User Bob environment
        asset_as_bob = self.asset.with_user(self.user_bob)

        # Odoo should raise AccessError when Bob tries to read
        with self.assertRaises(AccessError, msg="Bob should not be able to read assets."):
            _ = asset_as_bob.name

    def test_write_access_denied(self):
        """ I verify that a user cannot modify vital metrics without permissions. """
        asset_as_bob = self.asset.with_user(self.user_bob)

        with self.assertRaises(AccessError, msg="Bob should not be able to write to assets."):
            asset_as_bob.write({'current_temperature': 100.0})
