package com.aegis.scamfirewall.features.dashboard

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.History
import androidx.compose.material.icons.rounded.Mic
import androidx.compose.material.icons.automirrored.rounded.TextSnippet
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.aegis.scamfirewall.core.theme.AccentGreen
import com.aegis.scamfirewall.core.theme.AccentOrange
import com.aegis.scamfirewall.core.theme.AccentRed
import com.aegis.scamfirewall.core.theme.PrimaryBlue

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    onNavigate: (String) -> Unit
) {
    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = {
                    Text(
                        text = "Aegis Scam Firewall",
                        fontWeight = FontWeight.Bold
                    )
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = Color.Transparent
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
        ) {
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
                modifier = Modifier.fillMaxSize()
            ) {
                item {
                    FeatureCard(
                        title = "Intent Analysis",
                        description = "Analyze messages and detect malicious intent.",
                        icon = Icons.AutoMirrored.Rounded.TextSnippet,
                        accentColor = PrimaryBlue,
                        onClick = { onNavigate("intent") }
                    )
                }
                item {
                    FeatureCard(
                        title = "Document Scan",
                        description = "Scan contracts and PDFs for extreme clauses.",
                        icon = Icons.Rounded.Description,
                        accentColor = AccentOrange,
                        onClick = { onNavigate("scan") }
                    )
                }
                item {
                    FeatureCard(
                        title = "Live Audio Monitor",
                        description = "Detect deepfakes and AI voice synthesis.",
                        icon = Icons.Rounded.Mic,
                        accentColor = AccentRed,
                        onClick = { onNavigate("live") }
                    )
                }
                item {
                    FeatureCard(
                        title = "Threat History",
                        description = "Review recent AI threat analysis logs.",
                        icon = Icons.Rounded.History,
                        accentColor = AccentGreen,
                        onClick = { onNavigate("history") }
                    )
                }
            }
        }
    }
}

@Composable
fun FeatureCard(
    title: String,
    description: String,
    icon: ImageVector,
    accentColor: Color,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp)
            .clickable { onClick() },
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                tint = accentColor,
                modifier = Modifier.size(48.dp)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )
        }
    }
}
