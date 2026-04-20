import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/history_provider.dart';
import '../../../shared/widgets/loading_state_view.dart';
import '../../../shared/widgets/error_state_view.dart';
import '../../../shared/widgets/empty_state_view.dart';

class HistoryScreen extends ConsumerWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final historyAsync = ref.watch(historyProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Threat History Logs'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(historyProvider),
          )
        ],
      ),
      body: historyAsync.when(
        data: (logs) {
          if (logs.isEmpty) {
            return const EmptyStateView(
              message: 'No threats detected yet. All clear!',
              icon: Icons.shield,
            );
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16.0),
            itemCount: logs.length,
            separatorBuilder: (_, __) => const Divider(),
            itemBuilder: (context, index) {
              final log = logs[index];
              return ListTile(
                leading: CircleAvatar(
                  backgroundColor: Colors.red.shade100,
                  child: const Icon(Icons.security, color: Colors.red),
                ),
                title: Text(log.threatType, style: const TextStyle(fontWeight: FontWeight.bold)),
                subtitle: Text(log.details),
                trailing: Text(
                  log.timestamp.length > 10 ? log.timestamp.substring(0, 10) : log.timestamp, 
                  style: const TextStyle(fontSize: 12),
                ),
              );
            },
          );
        },
        loading: () => const LoadingStateView(message: 'Fetching threat logs...'),
        error: (error, _) => ErrorStateView(
          errorMessage: error.toString(),
          onRetry: () => ref.invalidate(historyProvider),
        ),
      ),
    );
  }
}
