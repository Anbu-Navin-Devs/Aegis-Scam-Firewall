import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/live_audio_service.dart';
import '../../models/deepfake_response.dart';

// Singleton for LiveAudioService
final liveAudioServiceProvider = Provider<LiveAudioService>((ref) {
  final service = LiveAudioService();
  ref.onDispose(() => service.disconnect());
  return service;
});

// StreamProvider that the UI can listen to for real-time deepfake frames
final deepfakeStreamProvider = StreamProvider<DeepfakeResponse>((ref) {
  final service = ref.watch(liveAudioServiceProvider);
  return service.threatStream;
});
