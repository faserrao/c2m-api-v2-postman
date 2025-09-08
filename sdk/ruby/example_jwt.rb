#!/usr/bin/env ruby

# C2M API Ruby SDK Example with JWT Authentication

require 'openapi_client'
require 'net/http'
require 'json'
require 'time'
require 'uri'

class C2MClient
  attr_reader :client_id, :client_secret, :base_url
  
  def initialize(client_id, client_secret, base_url = 'https://api.c2m.com/v2')
    @client_id = client_id
    @client_secret = client_secret
    @base_url = base_url
    @auth_url = base_url
    @long_token = nil
    @short_token = nil
    @token_expiry = nil
  end
  
  def get_long_token
    uri = URI("#{@auth_url}/auth/tokens/long")
    
    request_body = {
      grant_type: 'client_credentials',
      client_id: @client_id,
      client_secret: @client_secret,
      scopes: ['jobs:submit', 'jobs:read', 'templates:read'],
      ttl_seconds: 2592000 # 30 days
    }
    
    req = Net::HTTP::Post.new(uri)
    req['Content-Type'] = 'application/json'
    req.body = request_body.to_json
    
    response = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) do |http|
      http.request(req)
    end
    
    raise "Failed to get long token: #{response.code}" unless response.is_a?(Net::HTTPSuccess)
    
    data = JSON.parse(response.body)
    @long_token = data['access_token']
    puts "Long-term token obtained: #{data['token_id']}"
    @long_token
  end
  
  def get_short_token
    get_long_token unless @long_token
    
    uri = URI("#{@auth_url}/auth/tokens/short")
    
    request_body = {
      scopes: ['jobs:submit']
    }
    
    req = Net::HTTP::Post.new(uri)
    req['Content-Type'] = 'application/json'
    req['Authorization'] = "Bearer #{@long_token}"
    req.body = request_body.to_json
    
    response = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) do |http|
      http.request(req)
    end
    
    raise "Failed to get short token: #{response.code}" unless response.is_a?(Net::HTTPSuccess)
    
    data = JSON.parse(response.body)
    @short_token = data['access_token']
    @token_expiry = Time.parse(data['expires_at'])
    puts "Short-term token obtained: #{data['token_id']}"
    @short_token
  end
  
  def ensure_authenticated
    if @short_token.nil? || Time.now >= @token_expiry - 60 # 1 minute buffer
      get_short_token
    end
    @short_token
  end
  
  def create_api_client
    token = ensure_authenticated
    
    # Configure the API client
    OpenapiClient.configure do |config|
      config.host = @base_url.sub(/^https?:\/\//, '')
      config.scheme = @base_url.start_with?('https') ? 'https' : 'http'
      config.access_token = token
    end
    
    OpenapiClient::ApiClient.new
  end
  
  def submit_job(job_params, retry_on_auth_error: true)
    api_client = create_api_client
    api = OpenapiClient::DefaultApi.new(api_client)
    
    begin
      api.submit_single_doc_with_template_params(job_params)
    rescue OpenapiClient::ApiError => e
      if (e.code == 401 || e.code == 403) && retry_on_auth_error
        # Token expired, refresh and retry
        @short_token = nil
        submit_job(job_params, retry_on_auth_error: false)
      else
        raise
      end
    end
  end
end

# Usage example
if __FILE__ == $0
  client = C2MClient.new(
    'your-client-id',
    'your-client-secret'
  )
  
  job_params = {
    template_id: 'standard-letter',
    document_url: 'https://example.com/document.pdf',
    recipients: [{
      name: 'John Doe',
      address: {
        line1: '123 Main St',
        city: 'New York',
        state: 'NY',
        zip: '10001'
      }
    }]
  }
  
  begin
    result = client.submit_job(job_params)
    puts "Job submitted: #{result}"
  rescue => e
    puts "Error: #{e.message}"
  end
end