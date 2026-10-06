package com.aegis.scamfirewall.core.config

object AppConfig {
    private val isEmulator: Boolean
        get() = (android.os.Build.FINGERPRINT.startsWith("generic")
                || android.os.Build.MODEL.contains("google_sdk")
                || android.os.Build.MODEL.contains("Emulator")
                || android.os.Build.PRODUCT.contains("sdk")
                || android.os.Build.HARDWARE.contains("goldfish")
                || android.os.Build.HARDWARE.contains("ranchu"))

    private const val DEV_IP = "172.16.0.124"
    private const val DEV_PORT = "8000"

    val devBaseUrl: String
        get() = if (isEmulator) "http://10.0.2.2:$DEV_PORT" else "http://$DEV_IP:$DEV_PORT"

    val devWsUrl: String
        get() = if (isEmulator) "ws://10.0.2.2:$DEV_PORT" else "ws://$DEV_IP:$DEV_PORT"

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
