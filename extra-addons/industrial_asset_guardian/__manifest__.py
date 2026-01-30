{
    'name': "Industrial Asset Guardian (IAG)",
    'summary': "IoT-based Asset Health Monitoring System",
    'description': """
Industrial Asset Guardian (IAG)
================================

Central hub for industrial asset monitoring, bridging physical IoT sensors with Odoo's maintenance capabilities.

Key Features:
-------------
*   **Real-time Monitoring**: Tracking of Temperature and Vibration metrics.
*   **Predictive Health Score**: Algorithmic calculation of asset health (0-100%) based on configurable thresholds.
*   **Automated Maintenance**: Auto-generation of Maintenance Requests when assets report critical deviations.
*   **IoT API**: REST API endpoint for sensor data ingestion.
*   **Reactive UI**: 'Panic Gauge' widget for immediate visual status feedback.

    """,
    'author': "Hesfesto666",
    'website': "https://github.com/Hefesto66/industrial-asset-guardian-odoo",
    'category': 'Manufacturing/IoT',
    'version': '1.0',
    'depends': [
        'base',
        'mail',
        'maintenance',
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
