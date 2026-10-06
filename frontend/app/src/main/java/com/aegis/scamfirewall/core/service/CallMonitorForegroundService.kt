package com.aegis.scamfirewall.core.service

import android.annotation.SuppressLint
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Build
import android.os.IBinder
import android.util.Log
import com.aegis.scamfirewall.core.network.LiveAudioService
import com.aegis.scamfirewall.core.notification.AegisNotificationManager
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.collectLatest

class CallMonitorForegroundService : Service() {

    private val TAG = "AegisCallService"
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val liveAudioService = LiveAudioService()
    
    @Volatile
    private var isRecording = false
    private var audioRecord: AudioRecord? = null
    private var lastNotificationTimeMs = 0L

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "CallMonitorForegroundService created")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "CallMonitorForegroundService starting foreground monitoring...")

        val notification = AegisNotificationManager.buildCallMonitorNotification(this)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1001, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
        } else {
            startForeground(1001, notification)
        }

        if (!isRecording) {
            startLiveCallAudioMonitoring()
        }

        return START_STICKY
    }

    private fun startLiveCallAudioMonitoring() {
        isRecording = true
        liveAudioService.connect()

        // 1. Listen for backend deepfake detection verdicts
        serviceScope.launch {
            liveAudioService.threatFlow.collectLatest { response ->
                Log.d(TAG, "Audio stream verdict: isSynthetic=${response.isSynthetic}, score=${response.confidenceScore}")

                if (response.isSynthetic && response.confidenceScore >= 0.50f) {
                    val now = System.currentTimeMillis()
                    // 10-second cooldown between alert notifications to prevent notification flood
                    if (now - lastNotificationTimeMs > 10_000) {
                        lastNotificationTimeMs = now
                        AegisNotificationManager.notifyDeepfakeCallDetected(
                            context = applicationContext,
                            confidenceScore = response.confidenceScore,
                            details = response.rawDetails ?: "Abnormal acoustic uniformity and pitch stability"
                        )
                    }
                }
            }
        }

        // 2. Audio recording loop
        serviceScope.launch {
            runAudioCaptureLoop()
        }
    }

    @SuppressLint("MissingPermission")
    private fun runAudioCaptureLoop() {
        val sampleRate = 16000
        val channelConfig = AudioFormat.CHANNEL_IN_MONO
        val audioFormat = AudioFormat.ENCODING_PCM_16BIT
        val minBufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)
        val bufferSize = maxOf(minBufferSize, sampleRate * 2)

        try {
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                sampleRate,
                channelConfig,
                audioFormat,
                bufferSize
            )

            if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                Log.e(TAG, "Failed to initialize AudioRecord")
                return
            }

            audioRecord?.startRecording()
            Log.d(TAG, "AudioRecord started. Streaming to WebSocket...")

            val readBuffer = ShortArray(2048)

            while (isRecording) {
                val numRead = audioRecord?.read(readBuffer, 0, readBuffer.size) ?: 0
                if (numRead > 0) {
                    val floatSamples = FloatArray(numRead)
                    for (i in 0 until numRead) {
                        floatSamples[i] = readBuffer[i].toFloat() / 32768.0f
                    }
                    liveAudioService.streamAudio(floatSamples)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error in audio capture loop", e)
        } finally {
            try {
                audioRecord?.stop()
                audioRecord?.release()
            } catch (ignored: Exception) {}
            audioRecord = null
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "CallMonitorForegroundService stopping...")
        isRecording = false
        serviceScope.cancel()
        liveAudioService.disconnect()
        try {
            audioRecord?.stop()
            audioRecord?.release()
        } catch (ignored: Exception) {}
        audioRecord = null
    }
}
