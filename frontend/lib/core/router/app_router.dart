import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../features/dashboard/views/dashboard_screen.dart';
// Note: We will import the other feature screens here as we build them

final GoRouter appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const DashboardScreen(),
    ),
  ],
);
