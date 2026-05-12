<?php

declare(strict_types=1);

require_once __DIR__ . '/../src/PythonApiClient.php';

$customerId = trim((string) ($_GET['customer_id'] ?? 'CUSTOMER-001'));
$client = new PythonApiClient();

// Legacy UI delegates analytics retrieval to extracted Python API.
$response = $client->getCustomerDailyConsumption($customerId);
$rows = [];
if (isset($response['data']) && is_array($response['data'])) {
    $rows = $response['data'];
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Dashboard - Legacy Energy Portal</title>
</head>
<body>
    <h1>Customer Daily Consumption</h1>
    <p><a href="/legacy/">Back to portal</a></p>

    <form method="get" action="/legacy/dashboard.php">
        <label for="customer_id">Customer ID</label>
        <input id="customer_id" name="customer_id" value="<?= htmlspecialchars($customerId, ENT_QUOTES, 'UTF-8') ?>">
        <button type="submit">Load</button>
    </form>

    <p>Python API status: <?= (int) ($response['status_code'] ?? 0) ?></p>

    <table border="1" cellpadding="6" cellspacing="0">
        <thead>
            <tr>
                <th>Meter ID</th>
                <th>Customer ID</th>
                <th>Day</th>
                <th>Total kWh</th>
                <th>Reading Count</th>
                <th>Calculated At</th>
            </tr>
        </thead>
        <tbody>
            <?php if ($rows === []): ?>
                <tr>
                    <td colspan="6">No data</td>
                </tr>
            <?php else: ?>
                <?php foreach ($rows as $row): ?>
                    <tr>
                        <td><?= htmlspecialchars((string) ($row['meter_id'] ?? ''), ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars((string) ($row['customer_id'] ?? ''), ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars((string) ($row['day'] ?? ''), ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars((string) ($row['total_kwh'] ?? ''), ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars((string) ($row['reading_count'] ?? ''), ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars((string) ($row['calculated_at'] ?? ''), ENT_QUOTES, 'UTF-8') ?></td>
                    </tr>
                <?php endforeach; ?>
            <?php endif; ?>
        </tbody>
    </table>
</body>
</html>
