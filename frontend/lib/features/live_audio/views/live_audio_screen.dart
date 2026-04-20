import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/live_audio_provider.dart';
import '../../../shared/widgets/loading_state_view.dart';
import '../../../shared/widgets/error_state_view.dart';

class LiveAudioScreen extends ConsumerStatefulWidget {
  const LiveAudioScreen({super.key});

  @override
  ConsumerState<LiveAudioScreen> createState() => _LiveAudioScreenState();
}

class _LiveAudioScreenState extends ConsumerState<LiveAudioScreen> {
  @override
  void initState() {
    super.initState();
    // Connect to websocket when screen opens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(liveAudioServiceProvider).connect();
    });
  }

  @override
  Widget build(BuildContext context) {
    final streamState = ref.watch(deepfakeStreamProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Live Audio Monitor')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              streamState.when(
                data: (response) {
                  final confidence = (response.confidenceScore * 100).toStringAsFixed(1);
                  final isDeepfake = response.isSynthetic;
                  return Column(
                    children: [
                      Icon(
                        isDeepfake ? Icons.warning_amber : Icons.mic,
                        size: 100,
                        color: isDeepfake ? Colors.red : Colors.green,
                      ),
                      const SizedBox(height: 24),
                      Text(
                        isDeepfake ? 'DEEPFAKE DETECTED' : 'Audio is Authentic',
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          color: isDeepfake ? Colors.red : Colors.green,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Synthetic Confidence: $confidence%',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      if (response.flags.isNotEmpty) ...[
                        const SizedBox(height: 24),
                        const Text('Flags:', style: TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        Wrap(
                          spacing: 8,
                          children: response.flags.map((flag) => Chip(
                            label: Text(flag),
                            backgroundColor: Colors.red.shade100,
                          )).toList(),
                        )
                      ]
                    ],
                  );
                },
                loading: () => const LoadingStateView(message: 'Awaiting backend stream connection...'),
                error: (error, _) => ErrorStateView(
                  errorMessage: 'WebSocket Connection Failed: $error',
                  onRetry: () => ref.read(liveAudioServiceProvider).connect(),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
