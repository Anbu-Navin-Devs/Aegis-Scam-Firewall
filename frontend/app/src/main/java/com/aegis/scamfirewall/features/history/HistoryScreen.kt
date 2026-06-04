package com.aegis.scamfirewall.features.history

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.aegis.scamfirewall.core.network.ApiService
import com.aegis.scamfirewall.models.ThreatLog
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HistoryScreen(
    apiService: ApiService,
    onBack: () -> Unit
) {
    var logs by remember { mutableStateOf<List<ThreatLog>>(emptyList()) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMsg by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    fun fetchLogs() {
        scope.launch {
            isLoading = true
            errorMsg = null
            try {
                logs = apiService.getHistoryLogs()
            } catch (e: Exception) {
                errorMsg = e.localizedMessage ?: "Failed to fetch threat logs"
            } finally {
                isLoading = false
            }
        }
    }

    LaunchedEffect(Unit) {
        fetchLogs()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Threat History Logs") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { fetchLogs() }, enabled = !isLoading) {
                        Icon(imageVector = Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentAlignment = Alignment.Center
        ) {
            if (isLoading) {
                CircularProgressIndicator()
            } else if (errorMsg != null) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "Error: $errorMsg",
                        color = MaterialTheme.colorScheme.error,
                        modifier = Modifier.padding(16.dp)
                    )
                    Button(onClick = { fetchLogs() }) {
                        Text("Retry")
                    }
                }
            } else if (logs.isEmpty()) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center,
                    modifier = Modifier.fillMaxSize()
                ) {
                    Icon(
                        imageVector = Icons.Default.Shield,
                        contentDescription = null,
                        modifier = Modifier.size(72.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "No threats detected yet. All clear!",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(logs) { log ->
                        ThreatLogItem(log)
                    }
                }
            }
        }
    }
}

@Composable
fun ThreatLogItem(log: ThreatLog) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "${log.moduleType.uppercase()} - ${log.riskLevel}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = if (log.riskLevel.contains("SCAM") || log.riskLevel.contains("DEEPFAKE") || log.riskLevel.contains("HIGH")) Color.Red else Color.Green
                )
                
                // Standardize date printout
                val dateStr = if (log.timestamp.length > 10) log.timestamp.substring(0, 10) else log.timestamp
                Text(
                    text = dateStr,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            HorizontalDivider(color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.1f))
            Spacer(modifier = Modifier.height(8.dp))
            
            // Clean details printout
            val detailsMap = log.detailsJson
            val detailsText = when (log.moduleType.lowercase()) {
                "intent" -> {
                    val isScam = detailsMap["is_scam"] == true
                    val scamScore = (detailsMap["scam_score"] as? Number)?.toInt() ?: 0
                    val reason = detailsMap["reason"]?.toString() ?: ""
                    "Verdict: ${if (isScam) "SCAM" else "SAFE"} | Score: $scamScore/100\nReason: $reason"
                }
                "audio" -> {
                    val isDeepfake = detailsMap["is_deepfake"] == true
                    val score = (detailsMap["confidence_score"] as? Number)?.toDouble() ?: 0.0
                    val percent = String.format("%.1f", if (score > 1.0) score else score * 100f)
                    val details = detailsMap["analysis_details"]?.toString() ?: ""
                    "Verdict: ${if (isDeepfake) "DEEPFAKE" else "SAFE"} | Synthetic Confidence: $percent%\nDetails: $details"
                }
                "document" -> {
                    val risk = detailsMap["risk_level"]?.toString() ?: ""
                    val summary = detailsMap["summary"]?.toString() ?: ""
                    "Risk: $risk\nSummary: $summary"
                }
                else -> log.detailsJson.toString()
            }
            
            Text(
                text = detailsText,
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}
