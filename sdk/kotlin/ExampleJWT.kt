/**
 * C2M API Kotlin SDK Example with JWT Authentication
 */

package com.c2m.api.example

import com.c2m.api.apis.AuthApi
import com.c2m.api.apis.DefaultApi
import com.c2m.api.infrastructure.ApiClient
import com.c2m.api.infrastructure.ClientException
import com.c2m.api.infrastructure.ServerException
import com.google.gson.Gson
import kotlinx.coroutines.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.time.Instant
import java.time.temporal.ChronoUnit

class C2MClient(
    private val clientId: String,
    private val clientSecret: String,
    private val baseUrl: String = "https://api.c2m.com/v2"
) {
    private val httpClient = OkHttpClient()
    private val gson = Gson()
    private var longToken: String? = null
    private var shortToken: String? = null
    private var tokenExpiry: Instant? = null

    data class TokenResponse(
        val access_token: String,
        val token_id: String,
        val expires_at: String
    )

    private suspend fun getLongToken(): String = withContext(Dispatchers.IO) {
        val requestBody = mapOf(
            "grant_type" to "client_credentials",
            "client_id" to clientId,
            "client_secret" to clientSecret,
            "scopes" to listOf("jobs:submit", "jobs:read", "templates:read"),
            "ttl_seconds" to 2592000
        )

        val request = Request.Builder()
            .url("$baseUrl/auth/tokens/long")
            .post(
                gson.toJson(requestBody).toRequestBody("application/json".toMediaType())
            )
            .build()

        httpClient.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("Failed to get long token: ${response.code}")
            }

            val responseBody = response.body?.string() ?: throw IOException("Empty response")
            val tokenResponse = gson.fromJson(responseBody, TokenResponse::class.java)
            
            longToken = tokenResponse.access_token
            println("Long-term token obtained: ${tokenResponse.token_id}")
            tokenResponse.access_token
        }
    }

    private suspend fun getShortToken(): String = withContext(Dispatchers.IO) {
        if (longToken == null) {
            getLongToken()
        }

        val requestBody = mapOf(
            "scopes" to listOf("jobs:submit")
        )

        val request = Request.Builder()
            .url("$baseUrl/auth/tokens/short")
            .header("Authorization", "Bearer $longToken")
            .post(
                gson.toJson(requestBody).toRequestBody("application/json".toMediaType())
            )
            .build()

        httpClient.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("Failed to get short token: ${response.code}")
            }

            val responseBody = response.body?.string() ?: throw IOException("Empty response")
            val tokenResponse = gson.fromJson(responseBody, TokenResponse::class.java)
            
            shortToken = tokenResponse.access_token
            tokenExpiry = Instant.parse(tokenResponse.expires_at)
            println("Short-term token obtained: ${tokenResponse.token_id}")
            tokenResponse.access_token
        }
    }

    private suspend fun ensureAuthenticated(): String {
        val now = Instant.now()
        if (shortToken == null || tokenExpiry == null || now.isAfter(tokenExpiry?.minus(1, ChronoUnit.MINUTES))) {
            return getShortToken()
        }
        return shortToken!!
    }

    private suspend fun createApiClient(): ApiClient {
        val token = ensureAuthenticated()
        
        return ApiClient(baseUrl).apply {
            addDefaultHeader("Authorization", "Bearer $token")
        }
    }

    suspend fun submitJob(jobParams: Map<String, Any>): Any {
        return try {
            val apiClient = createApiClient()
            val api = DefaultApi(apiClient)
            api.submitSingleDocWithTemplateParams(jobParams)
        } catch (e: ClientException) {
            if (e.statusCode == 401 || e.statusCode == 403) {
                // Token expired, refresh and retry
                shortToken = null
                val apiClient = createApiClient()
                val api = DefaultApi(apiClient)
                api.submitSingleDocWithTemplateParams(jobParams)
            } else {
                throw e
            }
        }
    }
}

// Usage example
fun main() = runBlocking {
    try {
        val client = C2MClient(
            clientId = "your-client-id",
            clientSecret = "your-client-secret"
        )

        val jobParams = mapOf(
            "templateId" to "standard-letter",
            "documentUrl" to "https://example.com/document.pdf",
            "recipients" to listOf(
                mapOf(
                    "name" to "John Doe",
                    "address" to mapOf(
                        "line1" to "123 Main St",
                        "city" to "New York",
                        "state" to "NY",
                        "zip" to "10001"
                    )
                )
            )
        )

        val result = client.submitJob(jobParams)
        println("Job submitted: $result")
        
    } catch (e: Exception) {
        println("Error: ${e.message}")
    }
}