# Znote acc 2.0 Python back-end
# For paypal, testing on sandbox
# It adds coins onto the user accounts
from flask import Flask, request, jsonify
import mysql.connector
import requests
import os
import re
from datetime import datetime
from config import DB_CONFIG, PAYPAL, PAYPAL_UI, FLASK_PORT, ORDER_LOG_DIR, AMOUNT_TO_POINTS

app = Flask(__name__)
os.makedirs(ORDER_LOG_DIR, exist_ok=True)


def log_order(content):
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    with open(f'{ORDER_LOG_DIR}/order_{timestamp}.log', 'w') as f:
        f.write(content)


def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

@app.route('/api/paypal/config')
def get_paypal_config():
    from config import PAYPAL_UI
    return jsonify({
        'client_id': PAYPAL_UI['client_id'],
        'currency': PAYPAL_UI['currency']
    })

@app.route('/paypal-complete', methods=['POST'])
def paypal_complete():
    data = request.json
    log_order(f"RECEIVED JSON: {data}\n")

    username = data.get('username')
    amount_raw = data.get('amount')

    if not username or not amount_raw:
        return jsonify({'error': 'Invalid data'}), 400

    try:
        amount = float(amount_raw)
    except ValueError:
        return jsonify({'error': 'Invalid amount format'}), 400

    points = AMOUNT_TO_POINTS.get(amount)
    if not points:
        return jsonify({'error': 'Unknown amount'}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM accounts WHERE name = %s", (username,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'User not found'}), 404

        account_id = result[0]

        cursor.execute("UPDATE znote_accounts SET points = points + %s WHERE account_id = %s", (points, account_id))
        cursor.execute("""
            INSERT INTO znote_paypal (txn_id, email, accid, price, points, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            "web_checkout",
            "checkout-sdk@sandbox",
            account_id,
            amount,
            points,
            int(datetime.utcnow().timestamp())
        ))

        conn.commit()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Get price array from config
@app.route('/api/paypal/prices')
def get_paypal_prices():
    return jsonify(AMOUNT_TO_POINTS)

@app.route('/paypal-ipn', methods=['POST'])  # Matches https://yourdomain.com/paypal-ipn
def paypal_ipn():
    ipn_data = request.form.to_dict()
    verify_payload = {'cmd': '_notify-validate'}
    verify_payload.update(ipn_data)

    paypal_url = PAYPAL['sandbox_url'] if PAYPAL['sandbox'] else PAYPAL['live_url']
    verify_response = requests.post(paypal_url, data=verify_payload)

    log_data = f"IPN RECEIVED:\n{ipn_data}\nVerification: {verify_response.text}\n"

    if verify_response.text != 'VERIFIED':
        log_order(log_data + "ERROR: IPN not verified.\n")
        return "Invalid IPN", 400

    txn_id = ipn_data.get('txn_id')
    payment_status = ipn_data.get('payment_status')
    receiver_email = ipn_data.get('receiver_email')
    custom_username = ipn_data.get('custom')
    mc_gross_str = ipn_data.get('mc_gross', '0.00')

    try:
        mc_gross = round(float(mc_gross_str), 2)
    except ValueError:
        log_order(log_data + "ERROR: Invalid amount.\n")
        return "Invalid amount", 400

    if not txn_id or not is_valid_email(receiver_email) or not custom_username:
        log_order(log_data + "ERROR: Missing required fields or invalid email.\n")
        return "Invalid data", 400

    if payment_status != "Completed":
        log_order(log_data + "ERROR: Payment not completed.\n")
        return "Incomplete payment", 400

    if receiver_email != PAYPAL['receiver_email']:
        log_order(log_data + f"ERROR: Receiver email mismatch: {receiver_email}\n")
        return "Unauthorized receiver", 403

    # Match amount to points using tolerance
    def get_points_by_amount(amount):
        for a, p in AMOUNT_TO_POINTS.items():
            if abs(a - amount) < 0.01:
                return p
        return None

    points = get_points_by_amount(mc_gross)
    if not points:
        log_order(log_data + f"ERROR: Unknown amount {mc_gross} - available: {list(AMOUNT_TO_POINTS.keys())}\n")
        return "Unknown amount", 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM accounts WHERE name = %s", (custom_username,))
        result = cursor.fetchone()
        if not result:
            log_order(log_data + f"ERROR: User '{custom_username}' not found.\n")
            return "User not found", 404

        account_id = result[0]

        cursor.execute("UPDATE znote_accounts SET points = points + %s WHERE account_id = %s", (points, account_id))
        cursor.execute("""
            INSERT INTO znote_paypal (txn_id, email, accid, price, points)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            txn_id,
            receiver_email,
            account_id,
            mc_gross,
            points
        ))

        conn.commit()
        log_order(log_data + f"SUCCESS: {points} points added to '{custom_username}'.\n")
        return "OK", 200

    except Exception as e:
        log_order(log_data + f"ERROR: {e}\n")
        return "Server error", 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
