package com.aegis.scamfirewall.core.network

import com.aegis.scamfirewall.core.config.AppConfig
import com.aegis.scamfirewall.models.DeepfakeResponse
import com.google.gson.Gson
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import okhttp3.*
import okio.ByteString.Companion.toByteString
import java.nio.ByteBuffer
import java.nio.ByteOrder

class LiveAudioService {
    private val client = OkHttpClient()
    private var webSocket: WebSocket? = null
    private val gson = Gson()

    private val _threatFlow = MutableSharedFlow<DeepfakeResponse>(replay = 0)
    val threatFlow: SharedFlow<DeepfakeResponse> = _threatFlow

    private val _connectionState = MutableSharedFlow<Boolean>(replay = 1)
    val connectionState: SharedFlow<Boolean> = _connectionState

    private val _errorFlow = MutableSharedFlow<String>(replay = 0)
    val errorFlow: SharedFlow<String> = _errorFlow

    private var isConnected = false

    fun connect() {
        disconnect()

        val request = Request.Builder()
            .url("${AppConfig.wsUrl}/api/v1/live-audio/stream")
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                isConnected = true
                _connectionState.tryEmit(true)

                // 1. Send Handshake
                val handshake = mapOf("sample_rate" to 16000, "channels" to 1)
                webSocket.send(gson.toJson(handshake))
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    // Ignore lifecycle/system messages
                    if (text.contains("handshake_ok") || text.contains("session_end")) {
                        return
                    }
                    if (text.contains("error")) {
                        val errorMap = gson.fromJson(text, Map::class.java)
                        _errorFlow.tryEmit(errorMap["detail"]?.toString() ?: "Backend error")
                        return
                    }

                    val response = gson.fromJson(text, DeepfakeResponse::class.java)
                    _threatFlow.tryEmit(response)
                } catch (e: Exception) {
                    // Ignore parsing issues
                }
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                isConnected = false
                _connectionState.tryEmit(false)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                isConnected = false
                _connectionState.tryEmit(false)
                _errorFlow.tryEmit(t.message ?: "WebSocket failure")
            }
        })
    }

    fun streamAudio(audioSamples: FloatArray) {
        val socket = webSocket
        if (isConnected && socket != null) {
            // Convert FloatArray to little-endian float32 bytes (4 bytes per float)
            val byteBuffer = ByteBuffer.allocate(audioSamples.size * 4)
            byteBuffer.order(ByteOrder.LITTLE_ENDIAN)
            for (sample in audioSamples) {
                byteBuffer.putFloat(sample)
            }
            val byteString = byteBuffer.array().toByteString()
            socket.send(byteString)
        }
    }

    fun disconnect() {
        if (isConnected) {
            try {
                webSocket?.send("STOP")
            } catch (e: Exception) {
                // Ignore socket closures
            }
        }
        webSocket?.close(1000, "Goodbye")
        webSocket = null
        isConnected = false
        _connectionState.tryEmit(false)
    }
}
