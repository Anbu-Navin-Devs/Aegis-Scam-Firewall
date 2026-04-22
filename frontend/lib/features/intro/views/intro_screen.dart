import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';

class IntroScreen extends StatelessWidget {
  const IntroScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      body: Container(
        width: double.infinity,
        decoration: BoxDecoration(
          gradient: isDark
              ? const LinearGradient(
                  colors: [Color(0xFF0B0F19), Color(0xFF111827)],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                )
              : null, // Scafford bg handles light mode correctly
        ),
        child: SafeArea(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Spacer(),
              const Icon(
                Icons.security_rounded,
                size: 80,
                color: AppTheme.mBlue,
              ),
              const SizedBox(height: 24),
              Text(
                'Aegis Scam Firewall',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 40.0),
                child: Text(
                  'Smart protection against scams, fraud, and malicious threats',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: Colors.grey.shade500,
                      ),
                  textAlign: TextAlign.center,
                ),
              ),
              const Spacer(),
              // CTA Button Container
              Padding(
                padding: const EdgeInsets.only(bottom: 40.0),
                child: Container(
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    boxShadow: isDark
                        ? [
                            BoxShadow(
                              color: AppTheme.mBlue.withOpacity(0.3),
                              blurRadius: 16,
                              spreadRadius: 2,
                            )
                          ]
                        : null,
                  ),
                  child: FloatingActionButton(
                    onPressed: () {
                      context.go('/dashboard');
                    },
                    backgroundColor: AppTheme.mBlue,
                    foregroundColor: Colors.white,
                    elevation: isDark ? 0 : 4,
                    child: const Icon(Icons.arrow_forward_rounded, size: 30),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
