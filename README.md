# ZnoteACC PayPal API ( Sandbox )

A lightweight Flask-based PayPal payment integration for [Znote AAC 2.0](https://github.com/Znote/ZnoteAAC/tree/v2), designed to work with Nginx.  
Handles payment confirmation, IPN verification, and database updates for account points.

---

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx
```

### 2. Assuming your app will live at /var/www/html/paypal:
```
sudo mkdir -p /var/www/html/paypal
cd /var/www/html/paypal
python3 -m venv venv
source venv/bin/activate
```

### 3. Create a requirements.txt file with:
```
flask
requests
mysql-connector-python
gunicorn
```

### 4. Then install:
```
pip install -r requirements.txt
```

### Running the server ( Development )
```
python app.py
```

### Running the server ( Production )
```
gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
```

### Optional: Configure Gunicorn with systemd
```
sudo nano /etc/systemd/system/paypal.service
```

### Add this into paypal.service
```
[Unit]
Description=Gunicorn instance for ZnoteACC PayPal API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/html/paypal
Environment="PATH=/var/www/html/paypal/venv/bin"
ExecStart=/var/www/html/paypal/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

### Then enable and start:
```
sudo systemctl daemon-reexec
sudo systemctl enable paypal
sudo systemctl start paypal
```

### Check status:
```
sudo systemctl status paypal
```
