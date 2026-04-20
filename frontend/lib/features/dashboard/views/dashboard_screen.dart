import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Aegis Scam Firewall', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
      ),
      body: GridView.count(
        padding: const EdgeInsets.all(16),
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        children: [
          _buildFeatureCard(
            context,
            title: 'Intent Analysis',
            icon: Icons.text_snippet,
            color: Colors.blue,
            route: '/intent', // Route Placeholder
          ),
          _buildFeatureCard(
            context,
            title: 'Document Scan',
            icon: Icons.document_scanner,
            color: Colors.orange,
            route: '/scan',  // Route Placeholder
          ),
          _buildFeatureCard(
            context,
            title: 'Live Audio Monitor',
            icon: Icons.mic,
            color: Colors.redAccent,
            route: '/live',  // Route Placeholder
          ),
          _buildFeatureCard(
            context,
            title: 'Threat History',
            icon: Icons.history,
            color: Colors.teal,
            route: '/history', // Route Placeholder
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureCard(BuildContext context, {required String title, required IconData icon, required Color color, required String route}) {
    return InkWell(
      onTap: () {
        context.push(route);
      },
      child: Card(
        elevation: 4,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 50, color: color),
            const SizedBox(height: 16),
            Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}
