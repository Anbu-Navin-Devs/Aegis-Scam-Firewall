package com.aegis.scamfirewall.features.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log
import com.aegis.scamfirewall.core.ml.LocalScamClassifier
import com.aegis.scamfirewall.core.network.ApiService
import com.aegis.scamfirewall.core.notification.AegisNotificationManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class SmsReceiver : BroadcastReceiver() {

    private val TAG = "AegisSmsReceiver"
    private val apiService = ApiService()

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
            return
        }

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
        if (messages.isNullOrEmpty()) {
            return
        }

        val pendingResult = goAsync()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Group multi-part SMS by sender address
                val messagesBySender = messages.groupBy { it.originatingAddress ?: "Unknown" }

                for ((sender, parts) in messagesBySender) {
                    val fullMessage = parts.joinToString("") { it.messageBody ?: "" }
                    if (fullMessage.isBlank()) continue

                    Log.d(TAG, "Intercepted incoming SMS from $sender (${fullMessage.length} chars)")

                    // 1. Tier-1: Instant On-Device ML / Heuristic Classification (< 2ms)
                    val localResult = LocalScamClassifier.classify(fullMessage)
                    Log.d(TAG, "Local classification: isScam=${localResult.isScam}, score=${localResult.scamScore}")

                    // If high confidence local scam, alert immediately without waiting for network!
                    if (localResult.isScam) {
                        AegisNotificationManager.notifyScamSmsDetected(
                            context = context,
                            sender = sender,
                            messageSnippet = fullMessage,
                            scamScore = localResult.scamScore,
                            reason = localResult.reason
                        )
                    }

                    // 2. Tier-2: Send to backend for Cognitive Deep Analysis (Llama 3.3) & ThreatLog persistence
                    try {
                        val cloudResponse = apiService.analyzeIntent(fullMessage)
                        Log.d(TAG, "Backend LLM response: is_scam=${cloudResponse.isScam}, score=${cloudResponse.scamScore}")

                        // If cloud caught a scam that local classifier missed (e.g. subtle zero-day scam)
                        if (!localResult.isScam && cloudResponse.isScam) {
                            AegisNotificationManager.notifyScamSmsDetected(
                                context = context,
                                sender = sender,
                                messageSnippet = fullMessage,
                                scamScore = cloudResponse.scamScore,
                                reason = cloudResponse.reason
                            )
                        }
                    } catch (e: Exception) {
                        Log.w(TAG, "Backend unreachable or timed out; relied on Tier-1 on-device ML: ${e.message}")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error processing incoming SMS", e)
            } finally {
                pendingResult.finish()
            }
        }
    }
}
