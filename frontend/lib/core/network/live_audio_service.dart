import 'dart:async';
import 'dart:typed_data';
import '../../models/deepfake_response.dart';

/// MOCK MODE: WebSocket backend is offline.
/// This service simulates live deepfake analysis results locally.
/// Swap back to the real WebSocket implementation when backend is reachable.
class LiveAudioService {
  final _deepfakeStreamController = StreamController<DeepfakeResponse>.broadcast();
  Timer? _mockTimer;
  int _tick = 0;

  Stream<DeepfakeResponse> get threatStream => _deepfakeStreamController.stream;

  void connect() {
    _mockTimer?.cancel();
    // Emit a new mock result every 3 seconds to simulate live analysis
    _mockTimer = Timer.periodic(const Duration(seconds: 3), (_) {
      _emitMockResponse();
    });
    // Emit first result immediately so the screen doesn't stay blank
    Future.delayed(const Duration(milliseconds: 800), _emitMockResponse);
  }

  void _emitMockResponse() {
    _tick++;
    // Alternate between clean and deepfake to simulate a live feed
    final isDeepfake = _tick % 3 == 0; // Every 3rd tick is a deepfake

    final response = DeepfakeResponse(
      timestamp: DateTime.now().toIso8601String(),
      isSynthetic: isDeepfake,
      confidenceScore: isDeepfake ? 0.885 : 0.12,
      flags: isDeepfake
          ? ['SPECTRAL_FLATNESS_ANOMALY', 'PITCH_STABILITY_UNIFORM', 'NO_BREATHING_PAUSES']
          : [],
    );

    if (!_deepfakeStreamController.isClosed) {
      _deepfakeStreamController.add(response);
    }
  }

  void streamAudio(Float32List audioBytes) {
    // No-op in mock mode
  }

  void disconnect() {
    _mockTimer?.cancel();
    _mockTimer = null;
  }

  void dispose() {
    disconnect();
    _deepfakeStreamController.close();
  }
}
