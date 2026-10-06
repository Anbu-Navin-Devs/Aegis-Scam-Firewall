package com.aegis.scamfirewall.core.notification

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.os.Build
import androidx.core.app.NotificationCompat
import com.aegis.scamfirewall.MainActivity

object AegisNotificationManager {

    const val CHANNEL_SCAM_ALERTS = "aegis_scam_alerts"
    const val CHANNEL_CALL_MONITOR = "aegis_call_monitor"

    private const val NOTIFICATION_ID_CALL_MONITOR = 1001
    private var alertNotificationId = 2000

    fun createNotificationChannels(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

            // 1. High-Priority Alert Channel for scam SMS and deepfake warnings (Heads-up alert)
            val alertChannel = NotificationChannel(
                CHANNEL_SCAM_ALERTS,
                "Aegis Scam & Threat Alerts",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Urgent alerts when a scam SMS or deepfake voice is detected"
                enableLights(true)
                lightColor = Color.RED
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 300, 150, 300)
                lockscreenVisibility = Notification.VISIBILITY_PUBLIC
            }

            // 2. Foreground Service Channel for ongoing call audio monitoring
            val serviceChannel = NotificationChannel(
                CHANNEL_CALL_MONITOR,
                "Aegis Background Call Protection",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Persistent notification while live call audio monitoring is active"
                enableVibration(false)
                enableLights(false)
            }

            notificationManager.createNotificationChannel(alertChannel)
            notificationManager.createNotificationChannel(serviceChannel)
        }
    }

    fun notifyScamSmsDetected(
        context: Context,
        sender: String,
        messageSnippet: String,
        scamScore: Int,
        reason: String
    ) {
        createNotificationChannels(context)
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val openIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra("route", "intent")
            putExtra("transcript", messageSnippet)
        }
        val pendingIntent = PendingIntent.getActivity(
            context,
            alertNotificationId,
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, CHANNEL_SCAM_ALERTS)
            .setSmallIcon(android.R.drawable.stat_notify_error)
            .setContentTitle("🚨 Scam SMS Blocked! (Risk: $scamScore/100)")
            .setContentText("From $sender: $messageSnippet")
            .setStyle(
                NotificationCompat.BigTextStyle()
                    .bigText("From: $sender\n\nMessage: \"$messageSnippet\"\n\nDetected Threat: $reason")
                    .setBigContentTitle("🚨 Scam SMS Detected (Score: $scamScore/100)")
                    .setSummaryText("Aegis Threat Guard")
            )
            .setColor(0xFFEB5757.toInt()) // Red alert accent
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setVibrate(longArrayOf(0, 400, 200, 400))
            .build()

        notificationManager.notify(alertNotificationId++, notification)
    }

    fun notifyDeepfakeCallDetected(
        context: Context,
        confidenceScore: Float,
        details: String
    ) {
        createNotificationChannels(context)
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val openIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra("route", "live")
        }
        val pendingIntent = PendingIntent.getActivity(
            context,
            alertNotificationId,
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val percentStr = String.format("%.1f", confidenceScore * 100f)

        val notification = NotificationCompat.Builder(context, CHANNEL_SCAM_ALERTS)
            .setSmallIcon(android.R.drawable.stat_notify_error)
            .setContentTitle("⚠️ DEEPFAKE VOICE DETECTED ($percentStr%)")
            .setContentText("Suspicious synthetic audio detected during call. Tap to inspect.")
            .setStyle(
                NotificationCompat.BigTextStyle()
                    .bigText("Aegis detected AI synthetic speech ($percentStr% confidence) on the active call.\n\nDiagnostic: $details\n\nCaution: Do not share OTPs, passwords, or initiate financial transfers.")
                    .setBigContentTitle("⚠️ Active Call Deepfake Warning!")
                    .setSummaryText("Aegis Voice Firewall")
            )
            .setColor(0xFFEB5757.toInt())
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_CALL)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setVibrate(longArrayOf(0, 500, 200, 500))
            .build()

        notificationManager.notify(alertNotificationId++, notification)
    }

    fun buildCallMonitorNotification(context: Context): Notification {
        createNotificationChannels(context)

        val openIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra("route", "live")
        }
        val pendingIntent = PendingIntent.getActivity(
            context,
            NOTIFICATION_ID_CALL_MONITOR,
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(context, CHANNEL_CALL_MONITOR)
            .setSmallIcon(android.R.drawable.stat_sys_speakerphone)
            .setContentTitle("Aegis Call Firewall Active")
            .setContentText("Monitoring live audio stream for synthetic deepfake voice")
            .setColor(0xFF2F80ED.toInt()) // Blue accent
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .build()
    }
}
