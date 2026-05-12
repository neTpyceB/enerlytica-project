<?php

declare(strict_types=1);

final class PythonApiClient
{
    private string $baseUrl;

    public function __construct(string $baseUrl = 'http://python-api:8000/api')
    {
        $this->baseUrl = rtrim($baseUrl, '/');
    }

    public function submitReading(array $payload): array
    {
        return $this->postJson('/readings', $payload);
    }

    private function postJson(string $path, array $payload): array
    {
        $content = json_encode($payload, JSON_UNESCAPED_SLASHES);
        if ($content === false) {
            return [
                'status_code' => 500,
                'data' => null,
                'error' => 'Failed to encode payload to JSON',
            ];
        }

        $context = stream_context_create([
            'http' => [
                'method' => 'POST',
                'header' => implode("\r\n", [
                    'Content-Type: application/json',
                    'Accept: application/json',
                ]) . "\r\n",
                'content' => $content,
                'timeout' => 10,
                'ignore_errors' => true,
            ],
        ]);

        $body = @file_get_contents($this->baseUrl . $path, false, $context);
        $responseHeaders = $http_response_header ?? [];
        $statusCode = $this->extractStatusCode($responseHeaders);

        if ($body === false) {
            return [
                'status_code' => $statusCode,
                'data' => null,
                'error' => 'Request failed',
            ];
        }

        $decoded = json_decode($body, true);

        return [
            'status_code' => $statusCode,
            'data' => $decoded,
            'raw_body' => $body,
            'error' => null,
        ];
    }

    private function extractStatusCode(array $headers): int
    {
        if ($headers === []) {
            return 0;
        }

        if (preg_match('/\s(\d{3})\s/', $headers[0], $matches) === 1) {
            return (int) $matches[1];
        }

        return 0;
    }
}
