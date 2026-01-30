{
    'name': "Industrial Asset Guardian (IAG)",
    'summary': "IoT-based Asset Health Monitoring System",
    'description': """
IAG - Industrial Asset Guardian
================================

I designed this module to act as a central hub for industrial asset monitoring.
It bridges the gap between physical IoT sensors and Odoo's maintenance capabilities.

Key Features:
-------------
*   **Real-time Monitoring**: Tracks Temperature and Vibration metrics.
*   **Predictive Health Score**: I implemented an algorithm that automatically calculates asset health (0-100%).
*   **Automated Maintenance**: I automatically generate official Odoo Maintenance Requests when assets report critical failure signs.
*   **IoT API**: Includes a REST API endpoint for sensor data ingestion.
*   **Reactive UI**: Features a custom 'Panic Gauge' widget built with Odoo OWL Framework for Critical visual feedback.

Author: Hesfesto666
    """,
    'author': "Hesfesto666",
    'website': "https://github.com/Hefesto66/industrial-asset-guardian-odoo?tab=readme-ov-file",
    'category': 'Manufacturing/IoT',
    'version': '1.0',
    'depends': [
        'base',
        'mail',  # I require this for the Chatter (Messaging history) features.
        'maintenance',  # I integrate with the official Maintenance module for workflow management.
        # 'mrp',      # I may uncomment this in the future to integrate with Manufacturing Orders.
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'industrial_asset_guardian/static/src/components/panic_gauge/panic_gauge.scss',
            'industrial_asset_guardian/static/src/components/panic_gauge/panic_gauge.xml',
            'industrial_asset_guardian/static/src/components/panic_gauge/panic_gauge.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
