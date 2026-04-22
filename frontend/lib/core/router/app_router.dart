import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../features/dashboard/views/dashboard_screen.dart';
import '../../features/intent_analysis/views/intent_screen.dart';
import '../../features/document_scan/views/scan_screen.dart';
import '../../features/threat_history/views/history_screen.dart';
import '../../features/live_audio/views/live_audio_screen.dart';
import '../../features/intro/views/intro_screen.dart';

final GoRouter appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const IntroScreen(),
    ),
    GoRoute(
      path: '/dashboard',
      pageBuilder: (context, state) => CustomTransitionPage(
        key: state.pageKey,
        child: const DashboardScreen(),
        transitionDuration: const Duration(milliseconds: 300),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return FadeTransition(opacity: animation, child: child);
        },
      ),
    ),
    GoRoute(
      path: '/intent',
      builder: (context, state) => const IntentScreen(),
    ),
    GoRoute(
      path: '/scan',
      builder: (context, state) => const ScanScreen(),
    ),
    GoRoute(
      path: '/history',
      builder: (context, state) => const HistoryScreen(),
    ),
    GoRoute(
      path: '/live',
      builder: (context, state) => const LiveAudioScreen(),
    ),
  ],
);