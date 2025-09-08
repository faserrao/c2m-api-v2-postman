/**
 * C2M API C# SDK Example with JWT Authentication
 */

using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using C2M.Api.Api;
using C2M.Api.Client;
using C2M.Api.Model;

namespace C2M.Api.Example
{
    public class C2MClient
    {
        private readonly string _clientId;
        private readonly string _clientSecret;
        private readonly string _baseUrl;
        private readonly HttpClient _httpClient;
        private string _longToken;
        private string _shortToken;
        private DateTime _tokenExpiry;

        public C2MClient(string clientId, string clientSecret, string baseUrl = "https://api.c2m.com/v2")
        {
            _clientId = clientId;
            _clientSecret = clientSecret;
            _baseUrl = baseUrl;
            _httpClient = new HttpClient();
        }

        private async Task<string> GetLongTokenAsync()
        {
            var request = new
            {
                grant_type = "client_credentials",
                client_id = _clientId,
                client_secret = _clientSecret,
                scopes = new[] { "jobs:submit", "jobs:read", "templates:read" },
                ttl_seconds = 2592000 // 30 days
            };

            var content = new StringContent(
                JsonConvert.SerializeObject(request),
                Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync($"{_baseUrl}/auth/tokens/long", content);
            response.EnsureSuccessStatusCode();

            var responseData = JsonConvert.DeserializeObject<JObject>(
                await response.Content.ReadAsStringAsync()
            );

            _longToken = responseData["access_token"].ToString();
            Console.WriteLine($"Long-term token obtained: {responseData["token_id"]}");
            return _longToken;
        }

        private async Task<string> GetShortTokenAsync()
        {
            if (string.IsNullOrEmpty(_longToken))
            {
                await GetLongTokenAsync();
            }

            var request = new
            {
                scopes = new[] { "jobs:submit" }
            };

            var content = new StringContent(
                JsonConvert.SerializeObject(request),
                Encoding.UTF8,
                "application/json"
            );

            _httpClient.DefaultRequestHeaders.Clear();
            _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_longToken}");

            var response = await _httpClient.PostAsync($"{_baseUrl}/auth/tokens/short", content);
            response.EnsureSuccessStatusCode();

            var responseData = JsonConvert.DeserializeObject<JObject>(
                await response.Content.ReadAsStringAsync()
            );

            _shortToken = responseData["access_token"].ToString();
            _tokenExpiry = DateTime.Parse(responseData["expires_at"].ToString());
            Console.WriteLine($"Short-term token obtained: {responseData["token_id"]}");
            return _shortToken;
        }

        private async Task<string> EnsureAuthenticatedAsync()
        {
            if (string.IsNullOrEmpty(_shortToken) || DateTime.UtcNow.AddMinutes(1) >= _tokenExpiry)
            {
                await GetShortTokenAsync();
            }
            return _shortToken;
        }

        private async Task<Configuration> CreateConfigurationAsync()
        {
            var token = await EnsureAuthenticatedAsync();
            
            var config = new Configuration();
            config.BasePath = _baseUrl;
            config.AccessToken = token;
            
            return config;
        }

        public async Task<object> SubmitJobAsync(Dictionary<string, object> jobParams)
        {
            var config = await CreateConfigurationAsync();
            var apiInstance = new DefaultApi(config);

            try
            {
                var result = await apiInstance.SubmitSingleDocWithTemplateParamsAsync(jobParams);
                return result;
            }
            catch (ApiException e)
            {
                if (e.ErrorCode == 401 || e.ErrorCode == 403)
                {
                    // Token expired, refresh and retry
                    _shortToken = null;
                    config = await CreateConfigurationAsync();
                    apiInstance = new DefaultApi(config);
                    var result = await apiInstance.SubmitSingleDocWithTemplateParamsAsync(jobParams);
                    return result;
                }
                throw;
            }
        }
    }

    class Program
    {
        static async Task Main(string[] args)
        {
            try
            {
                var client = new C2MClient(
                    "your-client-id",
                    "your-client-secret"
                );

                var jobParams = new Dictionary<string, object>
                {
                    ["templateId"] = "standard-letter",
                    ["documentUrl"] = "https://example.com/document.pdf",
                    ["recipients"] = new[]
                    {
                        new Dictionary<string, object>
                        {
                            ["name"] = "John Doe",
                            ["address"] = new Dictionary<string, object>
                            {
                                ["line1"] = "123 Main St",
                                ["city"] = "New York",
                                ["state"] = "NY",
                                ["zip"] = "10001"
                            }
                        }
                    }
                };

                var result = await client.SubmitJobAsync(jobParams);
                Console.WriteLine($"Job submitted: {JsonConvert.SerializeObject(result)}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"Error: {e.Message}");
            }
        }
    }
}