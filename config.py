# config.py

# Database settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'database_user',
    'password': 'database_pw',
    'database': 'database'
}

# PayPal settings
PAYPAL = {
    'sandbox': True,
    'sandbox_url': 'https://ipnpb.sandbox.paypal.com/cgi-bin/webscr',
    'live_url': 'https://ipnpb.paypal.com/cgi-bin/webscr',
    'receiver_email': 'sandbox@example.com' # sandbox
}

# Flask settings
FLASK_PORT = 5000

# Amount to points mapping
PAYPAL_UI = {
    'enabled': True,
    'client_id': 'YOUR_CLIENT_ID',
    'currency': 'EUR'
}

AMOUNT_TO_POINTS = {
    1.00: 45,
    10.00: 100,
    15.00: 165,
    20.00: 240,
    25.00: 325,
    30.00: 420,
    50.00: 560
}

# Log settings
ORDER_LOG_DIR = 'order_logs'

# IPN listener endpoint (used for documentation, not dynamic)
PAYPAL_IPN_URL = 'https://yourdomain.com/paypal-ipn'
