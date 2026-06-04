package com.aegis.scamfirewall.core.config

object AppConfig {
    // Set to true if testing on official Android Emulator (uses 10.0.2.2)
    private const val USE_EMULATOR = false

    private const val DEV_IP = "172.16.0.124"
    private const val DEV_PORT = "8000"

    const val devBaseUrl = if (USE_EMULATOR) "http://10.0.2.2:$DEV_PORT" else "http://$DEV_IP:$DEV_PORT"
    const val devWsUrl = if (USE_EMULATOR) "ws://10.0.2.2:$DEV_PORT" else "ws://$DEV_IP:$DEV_PORT"

    const val prodBaseUrl = "https://api.aegisfirewall.com"
    const val prodWsUrl = "wss://api.aegisfirewall.com"

    const val isProduction = false

    // Optional API key for backend client authorization (matching backend's AEGIS_API_KEY)
    const val aegisApiKey = ""

    val baseUrl: String
        get() = if (isProduction) prodBaseUrl else devBaseUrl

    val wsUrl: String
        get() = if (isProduction) prodWsUrl else devWsUrl
}
