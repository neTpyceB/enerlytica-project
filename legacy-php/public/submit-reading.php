<?php

declare(strict_types=1);

require_once __DIR__ . '/../src/PythonApiClient.php';
session_start();

$response = null;
$formData = [
    'meter_id' => '',
    'customer_id' => '',
    'timestamp' => date('c'),
    'kwh' => '',
    'quality' => 'measured',
    'external_id' => '',
];

if (!isset($_SESSION['csrf_token']) || !is_string($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
$csrfToken = $_SESSION['csrf_token'];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $postedCsrfToken = (string) ($_POST['csrf_token'] ?? '');
    if (!hash_equals($csrfToken, $postedCsrfToken)) {
        $response = [
            'status_code' => 403,
            'data' => null,
            'error' => 'Invalid CSRF token',
        ];
    } else {
        $formData['meter_id'] = trim((string) ($_POST['meter_id'] ?? ''));
        $formData['customer_id'] = trim((string) ($_POST['customer_id'] ?? ''));
        $formData['timestamp'] = trim((string) ($_POST['timestamp'] ?? ''));
        $formData['kwh'] = trim((string) ($_POST['kwh'] ?? ''));
        $formData['quality'] = trim((string) ($_POST['quality'] ?? 'measured'));
        $formData['external_id'] = trim((string) ($_POST['external_id'] ?? ''));

        // Legacy PHP form delegates smart-meter processing to extracted Python service.
        $payload = [
            'meter_id' => $formData['meter_id'],
            'customer_id' => $formData['customer_id'],
            'timestamp' => $formData['timestamp'],
            'kwh' => (float) $formData['kwh'],
            'source' => 'legacy_php',
            'quality' => $formData['quality'],
        ];

        if ($formData['external_id'] !== '') {
            $payload['external_id'] = $formData['external_id'];
        }

        $client = new PythonApiClient();
        $response = $client->submitReading($payload);
    }
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Submit Reading - Legacy Energy Portal</title>
</head>
<body>
    <h1>Submit Reading</h1>
    <p><a href="/legacy/">Back to portal</a></p>

    <form method="post" action="/legacy/submit-reading.php">
        <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($csrfToken, ENT_QUOTES, 'UTF-8') ?>">
        <p>
            <label for="meter_id">Meter ID</label><br>
            <input id="meter_id" name="meter_id" required value="<?= htmlspecialchars($formData['meter_id'], ENT_QUOTES, 'UTF-8') ?>">
        </p>
        <p>
            <label for="customer_id">Customer ID</label><br>
            <input id="customer_id" name="customer_id" required value="<?= htmlspecialchars($formData['customer_id'], ENT_QUOTES, 'UTF-8') ?>">
        </p>
        <p>
            <label for="timestamp">Timestamp (ISO with timezone)</label><br>
            <input id="timestamp" name="timestamp" required value="<?= htmlspecialchars($formData['timestamp'], ENT_QUOTES, 'UTF-8') ?>">
        </p>
        <p>
            <label for="kwh">kWh</label><br>
            <input id="kwh" name="kwh" type="number" step="0.0001" min="0" required value="<?= htmlspecialchars($formData['kwh'], ENT_QUOTES, 'UTF-8') ?>">
        </p>
        <p>
            <label for="quality">Quality</label><br>
            <select id="quality" name="quality" required>
                <option value="measured" <?= $formData['quality'] === 'measured' ? 'selected' : '' ?>>measured</option>
                <option value="estimated" <?= $formData['quality'] === 'estimated' ? 'selected' : '' ?>>estimated</option>
                <option value="corrected" <?= $formData['quality'] === 'corrected' ? 'selected' : '' ?>>corrected</option>
            </select>
        </p>
        <p>
            <label for="external_id">External ID (optional idempotency key)</label><br>
            <input id="external_id" name="external_id" value="<?= htmlspecialchars($formData['external_id'], ENT_QUOTES, 'UTF-8') ?>">
        </p>
        <p>
            <button type="submit">Submit Reading</button>
        </p>
    </form>

    <?php if ($response !== null): ?>
        <h2>Python API Response</h2>
        <p>Status Code: <?= (int) ($response['status_code'] ?? 0) ?></p>
        <pre><?= htmlspecialchars(json_encode($response, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), ENT_QUOTES, 'UTF-8') ?></pre>
    <?php endif; ?>
</body>
</html>
