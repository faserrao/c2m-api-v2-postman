<?php
/**
 * C2M API PHP SDK Example with JWT Authentication
 */

require_once(__DIR__ . '/vendor/autoload.php');

use C2M\Api\AuthApi;
use C2M\Api\DefaultApi;
use C2M\Configuration;
use C2M\ApiException;
use GuzzleHttp\Client;

class C2MClient {
    private $clientId;
    private $clientSecret;
    private $baseUrl;
    private $authUrl;
    private $longToken;
    private $shortToken;
    private $tokenExpiry;
    private $httpClient;
    
    public function __construct($clientId, $clientSecret, $baseUrl = 'https://api.c2m.com/v2') {
        $this->clientId = $clientId;
        $this->clientSecret = $clientSecret;
        $this->baseUrl = $baseUrl;
        $this->authUrl = $baseUrl;
        $this->httpClient = new Client(['timeout' => 30]);
    }
    
    private function getLongToken() {
        $response = $this->httpClient->post($this->authUrl . '/auth/tokens/long', [
            'json' => [
                'grant_type' => 'client_credentials',
                'client_id' => $this->clientId,
                'client_secret' => $this->clientSecret,
                'scopes' => ['jobs:submit', 'jobs:read', 'templates:read'],
                'ttl_seconds' => 2592000 // 30 days
            ]
        ]);
        
        $data = json_decode($response->getBody(), true);
        $this->longToken = $data['access_token'];
        echo "Long-term token obtained: " . $data['token_id'] . "\n";
        return $this->longToken;
    }
    
    private function getShortToken() {
        if (!$this->longToken) {
            $this->getLongToken();
        }
        
        $response = $this->httpClient->post($this->authUrl . '/auth/tokens/short', [
            'headers' => [
                'Authorization' => 'Bearer ' . $this->longToken
            ],
            'json' => [
                'scopes' => ['jobs:submit']
            ]
        ]);
        
        $data = json_decode($response->getBody(), true);
        $this->shortToken = $data['access_token'];
        $this->tokenExpiry = new DateTime($data['expires_at']);
        echo "Short-term token obtained: " . $data['token_id'] . "\n";
        return $this->shortToken;
    }
    
    private function ensureAuthenticated() {
        $now = new DateTime();
        $buffer = clone $now;
        $buffer->modify('+1 minute');
        
        if (!$this->shortToken || !$this->tokenExpiry || $buffer >= $this->tokenExpiry) {
            $this->getShortToken();
        }
        
        return $this->shortToken;
    }
    
    private function createApiClient() {
        $token = $this->ensureAuthenticated();
        
        $config = Configuration::getDefaultConfiguration();
        $config->setHost($this->baseUrl);
        $config->setAccessToken($token);
        
        return new GuzzleHttp\Client();
    }
    
    public function submitJob($jobParams) {
        $apiInstance = new DefaultApi(
            $this->createApiClient(),
            Configuration::getDefaultConfiguration()->setAccessToken($this->ensureAuthenticated())
        );
        
        try {
            $result = $apiInstance->submitSingleDocWithTemplateParams($jobParams);
            return $result;
        } catch (ApiException $e) {
            if ($e->getCode() == 401 || $e->getCode() == 403) {
                // Token expired, refresh and retry
                $this->shortToken = null;
                $apiInstance = new DefaultApi(
                    $this->createApiClient(),
                    Configuration::getDefaultConfiguration()->setAccessToken($this->ensureAuthenticated())
                );
                return $apiInstance->submitSingleDocWithTemplateParams($jobParams);
            }
            throw $e;
        }
    }
}

// Usage example
try {
    $client = new C2MClient(
        'your-client-id',
        'your-client-secret'
    );
    
    $jobParams = [
        'templateId' => 'standard-letter',
        'documentUrl' => 'https://example.com/document.pdf',
        'recipients' => [[
            'name' => 'John Doe',
            'address' => [
                'line1' => '123 Main St',
                'city' => 'New York',
                'state' => 'NY',
                'zip' => '10001'
            ]
        ]]
    ];
    
    $result = $client->submitJob($jobParams);
    echo "Job submitted: " . json_encode($result) . "\n";
    
} catch (Exception $e) {
    echo 'Error: ' . $e->getMessage() . "\n";
}