import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/live_audio_service.dart';
import '../../models/deepfake_response.dart';

// AutoDispose so it cleans up when the screen is closed
final liveAudioServiceProvider = Provider.autoDispose<LiveAudioService>((ref) {
  final service = LiveAudioService();
  ref.onDispose(() => service.dispose());
  return service;
});

final deepfakeStreamProvider = StreamProvider.autoDispose<DeepfakeResponse>((ref) {
  final service = ref.watch(liveAudioServiceProvider);
  return service.threatStream;
});
