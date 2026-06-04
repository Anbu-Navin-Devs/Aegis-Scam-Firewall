package com.aegis.scamfirewall

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.aegis.scamfirewall.core.network.ApiService
import com.aegis.scamfirewall.core.network.LiveAudioService
import com.aegis.scamfirewall.core.theme.AegisTheme
import com.aegis.scamfirewall.features.dashboard.DashboardScreen
import com.aegis.scamfirewall.features.document.DocumentScanScreen
import com.aegis.scamfirewall.features.history.HistoryScreen
import com.aegis.scamfirewall.features.intent.IntentScreen
import com.aegis.scamfirewall.features.live.LiveAudioScreen

class MainActivity : ComponentActivity() {
    private val apiService = ApiService()
    private val liveAudioService = LiveAudioService()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AegisTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()
                    NavHost(navController = navController, startDestination = "dashboard") {
                        composable("dashboard") {
                            DashboardScreen(
                                onNavigate = { route -> navController.navigate(route) }
                            )
                        }
                        composable("intent") {
                            IntentScreen(
                                apiService = apiService,
                                onBack = { navController.popBackStack() }
                            )
                        }
                        composable("scan") {
                            DocumentScanScreen(
                                apiService = apiService,
                                onBack = { navController.popBackStack() }
                            )
                        }
                        composable("live") {
                            LiveAudioScreen(
                                liveAudioService = liveAudioService,
                                onBack = { navController.popBackStack() }
                            )
                        }
                        composable("history") {
                            HistoryScreen(
                                apiService = apiService,
                                onBack = { navController.popBackStack() }
                            )
                        }
                    }
                }
            }
        }
    }
}
