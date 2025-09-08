/**
 * C2M API Swift SDK Example with JWT Authentication
 */

import Foundation
import OpenAPIClient

class C2MClient {
    private let clientId: String
    private let clientSecret: String
    private let baseURL: String
    private var longToken: String?
    private var shortToken: String?
    private var tokenExpiry: Date?
    
    init(clientId: String, clientSecret: String, baseURL: String = "https://api.c2m.com/v2") {
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.baseURL = baseURL
    }
    
    private func getLongToken(completion: @escaping (Result<String, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/auth/tokens/long")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "grant_type": "client_credentials",
            "client_id": clientId,
            "client_secret": clientSecret,
            "scopes": ["jobs:submit", "jobs:read", "templates:read"],
            "ttl_seconds": 2592000 // 30 days
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let accessToken = json["access_token"] as? String,
                  let tokenId = json["token_id"] as? String else {
                completion(.failure(NSError(domain: "C2MClient", code: 1, userInfo: [NSLocalizedDescriptionKey: "Failed to parse token response"])))
                return
            }
            
            self?.longToken = accessToken
            print("Long-term token obtained: \(tokenId)")
            completion(.success(accessToken))
        }.resume()
    }
    
    private func getShortToken(completion: @escaping (Result<String, Error>) -> Void) {
        if longToken == nil {
            getLongToken { [weak self] result in
                switch result {
                case .success:
                    self?.getShortToken(completion: completion)
                case .failure(let error):
                    completion(.failure(error))
                }
            }
            return
        }
        
        let url = URL(string: "\(baseURL)/auth/tokens/short")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(longToken!)", forHTTPHeaderField: "Authorization")
        
        let body: [String: Any] = [
            "scopes": ["jobs:submit"]
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let accessToken = json["access_token"] as? String,
                  let tokenId = json["token_id"] as? String,
                  let expiresAt = json["expires_at"] as? String else {
                completion(.failure(NSError(domain: "C2MClient", code: 2, userInfo: [NSLocalizedDescriptionKey: "Failed to parse short token response"])))
                return
            }
            
            let formatter = ISO8601DateFormatter()
            self?.shortToken = accessToken
            self?.tokenExpiry = formatter.date(from: expiresAt)
            print("Short-term token obtained: \(tokenId)")
            completion(.success(accessToken))
        }.resume()
    }
    
    private func ensureAuthenticated(completion: @escaping (Result<String, Error>) -> Void) {
        let now = Date()
        let buffer = now.addingTimeInterval(60) // 1 minute buffer
        
        if shortToken == nil || tokenExpiry == nil || buffer >= tokenExpiry! {
            getShortToken(completion: completion)
        } else {
            completion(.success(shortToken!))
        }
    }
    
    private func configureAPI(token: String) {
        OpenAPIClientAPI.basePath = baseURL
        OpenAPIClientAPI.customHeaders["Authorization"] = "Bearer \(token)"
    }
    
    func submitJob(jobParams: [String: Any], completion: @escaping (Result<Any, Error>) -> Void) {
        ensureAuthenticated { [weak self] result in
            switch result {
            case .success(let token):
                self?.configureAPI(token: token)
                
                // Create job submission request
                // Note: This would need to be adapted based on the actual Swift SDK model classes
                DefaultAPI.submitSingleDocWithTemplateParams(body: jobParams) { response, error in
                    if let error = error as NSError? {
                        if error.code == 401 || error.code == 403 {
                            // Token expired, refresh and retry
                            self?.shortToken = nil
                            self?.submitJob(jobParams: jobParams, completion: completion)
                        } else {
                            completion(.failure(error))
                        }
                    } else if let response = response {
                        completion(.success(response))
                    }
                }
                
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
}

// Usage example
class ExampleUsage {
    static func main() {
        let client = C2MClient(
            clientId: "your-client-id",
            clientSecret: "your-client-secret"
        )
        
        let jobParams: [String: Any] = [
            "templateId": "standard-letter",
            "documentUrl": "https://example.com/document.pdf",
            "recipients": [[
                "name": "John Doe",
                "address": [
                    "line1": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001"
                ]
            ]]
        ]
        
        client.submitJob(jobParams: jobParams) { result in
            switch result {
            case .success(let response):
                print("Job submitted: \(response)")
            case .failure(let error):
                print("Error: \(error.localizedDescription)")
            }
        }
    }
}