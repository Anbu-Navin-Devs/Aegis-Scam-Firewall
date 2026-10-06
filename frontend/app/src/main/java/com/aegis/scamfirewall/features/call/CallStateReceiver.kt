package com.aegis.scamfirewall.features.call

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import android.telephony.TelephonyManager
import android.util.Log
import com.aegis.scamfirewall.core.service.CallMonitorForegroundService

class CallStateReceiver : BroadcastReceiver() {

    private val TAG = "AegisCallReceiver"

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != TelephonyManager.ACTION_PHONE_STATE_CHANGED) {
            return
        }

        val stateStr = intent.getStringExtra(TelephonyManager.EXTRA_STATE) ?: return
        Log.d(TAG, "Phone State Changed: $stateStr")

        when (stateStr) {
            TelephonyManager.EXTRA_STATE_OFFHOOK -> {
                // Call started or answered -> Start background call audio monitor service
                Log.d(TAG, "Call active (OFFHOOK). Starting CallMonitorForegroundService...")
                val serviceIntent = Intent(context, CallMonitorForegroundService::class.java)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    context.startForegroundService(serviceIntent)
                } else {
                    context.startService(serviceIntent)
                }
            }

            TelephonyManager.EXTRA_STATE_IDLE -> {
                // Call ended or rejected -> Stop background monitor
                Log.d(TAG, "Call ended (IDLE). Stopping CallMonitorForegroundService...")
                val serviceIntent = Intent(context, CallMonitorForegroundService::class.java)
                context.stopService(serviceIntent)
            }

            TelephonyManager.EXTRA_STATE_RINGING -> {
                Log.d(TAG, "Phone ringing...")
            }
        }
    }
}
