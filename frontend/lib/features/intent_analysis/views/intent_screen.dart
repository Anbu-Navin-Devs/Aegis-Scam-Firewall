import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/intent_provider.dart';
import '../../../shared/widgets/loading_state_view.dart';
import '../../../shared/widgets/error_state_view.dart';

class IntentScreen extends ConsumerStatefulWidget {
  const IntentScreen({super.key});

  @override
  ConsumerState<IntentScreen> createState() => _IntentScreenState();
}

class _IntentScreenState extends ConsumerState<IntentScreen> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final intentState = ref.watch(intentProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Intent Analysis')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _controller,
              decoration: const InputDecoration(
                labelText: 'Paste message or transcript here...',
                border: OutlineInputBorder(),
              ),
              maxLines: 5,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                FocusScope.of(context).unfocus();
                ref.read(intentProvider.notifier).analyzeIntent(_controller.text);
              },
              icon: const Icon(Icons.analytics),
              label: const Text('Analyze Intent'),
            ),
            const SizedBox(height: 24),
            Expanded(
              child: intentState.when(
                data: (response) {
                  if (response == null) return const SizedBox.shrink();
                  final isScam = response.isScam;
                  return Card(
                    color: isScam ? Colors.red.shade50 : Colors.green.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const SizedBox(height: 16),
                          Text(
                            isScam ? '⚠️ SCAM DETECTED' : '✅ SAFE',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              color: isScam ? Colors.red : Colors.green,
                              fontWeight: FontWeight.bold,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Scam Score: ${response.scamScore}/100',
                            style: Theme.of(context).textTheme.titleMedium,
                            textAlign: TextAlign.center,
                          ),
                          const Divider(),
                          Text(
                            response.reason,
                            style: Theme.of(context).textTheme.bodyMedium,
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  );
                },
                loading: () => const LoadingStateView(message: 'Analyzing intent...'),
                error: (error, _) => ErrorStateView(
                  errorMessage: error.toString(),
                  onRetry: () => ref.read(intentProvider.notifier).analyzeIntent(_controller.text),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
