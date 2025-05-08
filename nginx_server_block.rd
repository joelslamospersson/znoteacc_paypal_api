# Paypal-ipn + logging
location /paypal-ipn {
  access_log /var/log/nginx/paypal-ipn.log;
  error_log /var/log/nginx/paypal-ipn_error.log;
  proxy_pass http://127.0.0.1:5000/paypal-ipn;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
}

location /api/paypal/config {
  proxy_pass http://127.0.0.1:5000/api/paypal/config;
  proxy_set_header Host $host;
}

location /paypal-complete {
  proxy_pass http://127.0.0.1:5000/paypal-complete;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
}

# Fetch price data
location /api/paypal/prices {
  proxy_pass http://127.0.0.1:5000/api/paypal/prices;
  proxy_set_header Host $host;
}
