<?php
require_once 'engine/init.php';
protect_page();
include 'layout/overall/header.php';

$username = $user_data['name'];
?>

<h1>Buy Points</h1>
<p>Select a package and pay with PayPal:</p>

<select id="point-package" class="form-control" style="max-width: 300px; margin-bottom: 20px;"></select>

<div id="paypal-button-container" style="min-height: 60px;"></div>

<script>
const username = <?= json_encode($username) ?>;

Promise.all([
    fetch('/api/paypal/config').then(res => res.json()),
    fetch('/api/paypal/prices').then(res => res.json())
]).then(([config, prices]) => {
    const select = document.getElementById('point-package');
    Object.entries(prices).forEach(([price, points]) => {
        const option = document.createElement('option');
        option.value = price;
        option.textContent = `${price} ${config.currency} - ${points} points`;
        select.appendChild(option);
    });

    const script = document.createElement('script');
    script.src = `https://www.paypal.com/sdk/js?client-id=${config.client_id}&currency=${config.currency}`;
    script.onload = () => {
        paypal.Buttons({
            createOrder: function(data, actions) {
                const amount = select.value;
                return actions.order.create({
                    purchase_units: [{
                        amount: { value: amount }
                    }]
                });
            },
            onApprove: function(data, actions) {
                const amount = select.value;
                return actions.order.capture().then(function(details) {
                    fetch('/paypal-complete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, amount })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            alert('✅ Points added to your account!');
                            location.reload();
                        } else {
                            alert('❌ Error: ' + data.error);
                        }
                    });
                });
            }
        }).render('#paypal-button-container');
    };
    document.head.appendChild(script);
}).catch(err => {
    console.error('Error loading PayPal or prices:', err);
    document.getElementById('paypal-button-container').innerText = 'Failed to load PayPal.';
});
</script>

<?php include 'layout/overall/footer.php'; ?>
