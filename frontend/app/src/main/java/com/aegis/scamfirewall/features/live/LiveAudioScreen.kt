package com.aegis.scamfirewall.features.live

import android.Manifest
import android.annotation.SuppressLint
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.MicOff
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.aegis.scamfirewall.core.network.LiveAudioService
import com.aegis.scamfirewall.core.theme.AlertGreenBg
import com.aegis.scamfirewall.core.theme.AlertRedBg
import com.aegis.scamfirewall.models.DeepfakeResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LiveAudioScreen(
    liveAudioService: LiveAudioService,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    
    var isConnected by remember { mutableStateOf(false) }
    var isRecording by remember { mutableStateOf(false) }
    var response by remember { mutableStateOf<DeepfakeResponse?>(null) }
    var errorMsg by remember { mutableStateOf<String?>(null) }
    var hasMicPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED
        )
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        hasMicPermission = granted
    }

    // Connect WebSocket on launch, disconnect on dispose
    DisposableEffect(Unit) {
        liveAudioService.connect()
        
        val jobConnection = scope.launch {
            liveAudioService.connectionState.collectLatest { connected ->
                isConnected = connected
            }
        }

        val jobThreats = scope.launch {
            liveAudioService.threatFlow.collectLatest { threat ->
                response = threat
                errorMsg = null
            }
        }

        val jobErrors = scope.launch {
            liveAudioService.errorFlow.collectLatest { error ->
                errorMsg = error
            }
        }

        onDispose {
            isRecording = false
            liveAudioService.disconnect()
            jobConnection.cancel()
            jobThreats.cancel()
            jobErrors.cancel()
        }
    }

    // Mic recording loop
    LaunchedEffect(isRecording) {
        if (isRecording) {
            withContext(Dispatchers.IO) {
                runRecordingLoop(liveAudioService) { isRecording }
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Live Audio Monitor") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            if (!hasMicPermission) {
                Icon(
                    imageVector = Icons.Default.MicOff,
                    contentDescription = null,
                    modifier = Modifier.size(100.dp),
                    tint = MaterialTheme.colorScheme.error
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "Microphone Permission Required",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(16.dp))
                Button(onClick = { permissionLauncher.launch(Manifest.permission.RECORD_AUDIO) }) {
                    Text("Grant Permission")
                }
                return@Scaffold
            }

            if (errorMsg != null) {
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
                    modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(imageVector = Icons.Default.Warning, contentDescription = "Error")
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(text = "Connection Failed", fontWeight = FontWeight.Bold)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(text = errorMsg!!)
                    }
                }
            }

            if (response != null) {
                val threat = response!!
                val isDeepfake = threat.isSynthetic
                val confidencePercentage = threat.confidenceScore * 100f
                val confidence = String.format("%.1f", confidencePercentage)

                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = if (isDeepfake) AlertRedBg else AlertGreenBg
                    ),
                    modifier = Modifier.fillMaxWidth().padding(bottom = 32.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            imageVector = if (isDeepfake) Icons.Default.Warning else Icons.Default.Mic,
                            contentDescription = null,
                            modifier = Modifier.size(80.dp),
                            tint = if (isDeepfake) Color.Red else Color.Green
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = if (isDeepfake) "DEEPFAKE DETECTED" else "Audio is Authentic",
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold,
                            color = if (isDeepfake) Color.Red else Color.Green,
                            textAlign = TextAlign.Center
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = "Synthetic Confidence: $confidence%",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.SemiBold,
                            textAlign = TextAlign.Center
                        )
                        
                        if (threat.flags.isNotEmpty()) {
                            Spacer(modifier = Modifier.height(16.dp))
                            Text("Flags:", fontWeight = FontWeight.Bold)
                            Spacer(modifier = Modifier.height(8.dp))
                            Row(
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                modifier = Modifier.fillMaxWidth(),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                threat.flags.forEach { flag ->
                                    SuggestionChip(
                                        onClick = {},
                                        label = { Text(flag) },
                                        colors = SuggestionChipDefaults.suggestionChipColors(
                                            containerColor = Color.Red.copy(alpha = 0.1f),
                                            labelColor = Color.Red
                                        )
                                    )
                                }
                            }
                        }
                    }
                }
            } else {
                Text(
                    text = if (isConnected) "Awaiting stream to begin..." else "Connecting to firewall...",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(48.dp))
            }

            // Connection/Record control
            FloatingActionButton(
                onClick = {
                    if (isConnected) {
                        isRecording = !isRecording
                    } else {
                        liveAudioService.connect()
                    }
                },
                containerColor = if (isRecording) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(80.dp)
            ) {
                Icon(
                    imageVector = if (isRecording) Icons.Default.MicOff else Icons.Default.Mic,
                    contentDescription = if (isRecording) "Stop Stream" else "Start Stream",
                    modifier = Modifier.size(36.dp),
                    tint = Color.White
                )
            }
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = if (isRecording) "STREAMING MICROPHONE" else "Tap Mic to Start Monitoring",
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold,
                color = if (isRecording) Color.Red else MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@SuppressLint("MissingPermission")
private fun runRecordingLoop(
    liveAudioService: LiveAudioService,
    isRecordingActive: () -> Boolean
) {
    val sampleRate = 16000
    val channelConfig = AudioFormat.CHANNEL_IN_MONO
    val audioFormat = AudioFormat.ENCODING_PCM_16BIT
    val minBufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)
    
    // Allocate 1-second buffer chunks to match backend expectations (16000 samples)
    val bufferSize = maxOf(minBufferSize, sampleRate * 2) 
    
    val recorder = AudioRecord(
        MediaRecorder.AudioSource.MIC,
        sampleRate,
        channelConfig,
        audioFormat,
        bufferSize
    )

    if (recorder.state != AudioRecord.STATE_INITIALIZED) {
        return
    }

    recorder.startRecording()
    
    // Read 2048 samples at a time to prevent high latency
    val readBuffer = ShortArray(2048)
    
    try {
        while (isRecordingActive()) {
            val numRead = recorder.read(readBuffer, 0, readBuffer.size)
            if (numRead > 0) {
                // Convert PCM 16-bit signed shorts (-32768 to 32767) to normalized floats (-1.0 to 1.0)
                val floatSamples = FloatArray(numRead)
                for (i in 0 until numRead) {
                    floatSamples[i] = readBuffer[i].toFloat() / 32768.0f
                }
                liveAudioService.streamAudio(floatSamples)
            }
        }
    } catch (e: Exception) {
        // Handle read anomalies
    } finally {
        recorder.stop()
        recorder.release()
    }
}
