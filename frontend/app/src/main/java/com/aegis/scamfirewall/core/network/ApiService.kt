package com.aegis.scamfirewall.core.network

import com.aegis.scamfirewall.core.config.AppConfig
import com.aegis.scamfirewall.models.DocumentScanResponse
import com.aegis.scamfirewall.models.IntentResponse
import com.aegis.scamfirewall.models.ThreatLog
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.IOException

class ApiException(val statusCode: Int, message: String) : Exception(message)

class ApiService {
    private val client = OkHttpClient()
    private val gson = Gson()

    private fun buildRequest(url: String, builderAction: Request.Builder.() -> Unit): Request {
        val builder = Request.Builder().url(url)
        if (AppConfig.aegisApiKey.isNotEmpty()) {
            builder.addHeader("X-Aegis-API-Key", AppConfig.aegisApiKey)
        }
        builder.builderAction()
        return builder.build()
    }

    suspend fun analyzeIntent(transcript: String): IntentResponse = withContext(Dispatchers.IO) {
        val json = gson.toJson(mapOf("transcript" to transcript))
        val body = json.toRequestBody("application/json; charset=utf-8".toMediaType())
        
        val request = buildRequest("${AppConfig.baseUrl}/api/v1/analyze/intent") {
            post(body)
        }

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw ApiException(response.code, "Failed to analyze intent: ${response.message}")
            }
            val bodyString = response.body?.string() ?: throw IOException("Empty response body")
            gson.fromJson(bodyString, IntentResponse::class.java)
        }
    }

    suspend fun scanDocument(filePath: String): DocumentScanResponse = withContext(Dispatchers.IO) {
        val file = File(filePath)
        if (!file.exists()) {
            throw IOException("File does not exist: $filePath")
        }

        val mediaType = when (file.extension.lowercase()) {
            "pdf" -> "application/pdf".toMediaType()
            "png" -> "image/png".toMediaType()
            "jpg", "jpeg" -> "image/jpeg".toMediaType()
            else -> "application/octet-stream".toMediaType()
        }

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "file",
                file.name,
                file.asRequestBody(mediaType)
            )
            .build()

        val request = buildRequest("${AppConfig.baseUrl}/api/v1/document/scan") {
            post(requestBody)
        }

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw ApiException(response.code, "Failed to scan document: ${response.message}")
            }
            val bodyString = response.body?.string() ?: throw IOException("Empty response body")
            gson.fromJson(bodyString, DocumentScanResponse::class.java)
        }
    }

    suspend fun getHistoryLogs(limit: Int = 20): List<ThreatLog> = withContext(Dispatchers.IO) {
        val request = buildRequest("${AppConfig.baseUrl}/api/v1/history/logs?limit=$limit") {
            get()
        }

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw ApiException(response.code, "Failed to fetch history logs: ${response.message}")
            }
            val bodyString = response.body?.string() ?: throw IOException("Empty response body")
            
            // The backend returns a page object: {"total": X, "skip": Y, "limit": Z, "logs": [...]}
            val responseMap = gson.fromJson<Map<String, Any>>(
                bodyString,
                object : TypeToken<Map<String, Any>>() {}.type
            )
            val logsListJson = responseMap["logs"] ?: return@withContext emptyList<ThreatLog>()
            
            val logsString = gson.toJson(logsListJson)
            gson.fromJson(
                logsString,
                object : TypeToken<List<ThreatLog>>() {}.type
            )
        }
    }
}
