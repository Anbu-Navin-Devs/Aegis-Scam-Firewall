import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../models/deepfake_response.dart';
import '../config/app_config.dart';
import '../constants/api_endpoints.dart';

class LiveAudioService {
  WebSocketChannel? _channel;
  final _deepfakeStreamController = StreamController<DeepfakeResponse>.broadcast();

  Stream<DeepfakeResponse> get threatStream => _deepfakeStreamController.stream;

  void connect() {
    _channel = WebSocketChannel.connect(
      Uri.parse('${AppConfig.wsUrl}${ApiEndpoints.liveAudioStream}')
    );
    
    // Handshake
    _channel!.sink.add(jsonEncode({'sample_rate': 16000}));

    _channel!.stream.listen(_onDataReceived, onError: _onError, onDone: _onDone);
  }

  void _onDataReceived(dynamic data) {
    try {
      final decoded = jsonDecode(data as String);
      final response = DeepfakeResponse.fromJson(decoded);
      _deepfakeStreamController.add(response);
    } catch (e) {
      print('WebSocket parsing error: $e');
    }
  }

  void _onError(error) {
    print('WebSocket error: $error');
  }

  void _onDone() {
    print('WebSocket closed');
  }

  void streamAudio(Float32List audioBytes) {
    if (_channel != null && _channel!.closeCode == null) {
      _channel!.sink.add(audioBytes.buffer.asUint8List());
    }
  }

  void disconnect() {
    _channel?.sink.close();
    _deepfakeStreamController.close();
  }
}
