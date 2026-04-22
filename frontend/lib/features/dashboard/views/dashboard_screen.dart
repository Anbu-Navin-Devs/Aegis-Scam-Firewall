import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';
import '../../../shared/widgets/modern_feature_card.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Aegis Scam Firewall', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      body: GridView.count(
        padding: const EdgeInsets.all(20),
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 0.85, // Adjust card height
        children: [
          ModernFeatureCard(
            title: 'Intent Analysis',
            description: 'Analyze messages and detect malicious intent.',
            icon: Icons.text_snippet_rounded,
            accentColor: AppTheme.mBlue,
            onTap: () => context.push('/intent'),
          ),
          ModernFeatureCard(
            title: 'Document Scan',
            description: 'Scan contracts and PDFs for extreme clauses.',
            icon: Icons.document_scanner_rounded,
            accentColor: AppTheme.mOrange,
            onTap: () => context.push('/scan'),
          ),
          ModernFeatureCard(
            title: 'Live Audio Monitor',
            description: 'Detect deepfakes and AI voice synthesis.',
            icon: Icons.mic_rounded,
            accentColor: AppTheme.mRed,
            onTap: () => context.push('/live'),
          ),
          ModernFeatureCard(
            title: 'Threat History',
            description: 'Review recent AI threat analysis logs.',
            icon: Icons.history_rounded,
            accentColor: AppTheme.mGreen,
            onTap: () => context.push('/history'),
          ),
        ],
      ),
    );
  }
}
