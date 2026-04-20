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
  bool _isConnecting = false;
  Timer? _reconnectTimer;

  Stream<DeepfakeResponse> get threatStream => _deepfakeStreamController.stream;

  void connect() {
    if (_isConnecting) return;
    _isConnecting = true;
    _reconnectTimer?.cancel();

    try {
      _channel = WebSocketChannel.connect(
        Uri.parse('${AppConfig.wsUrl}${ApiEndpoints.liveAudioStream}')
      );
      
      // Handshake immediately per backend protocol
      _channel!.sink.add(jsonEncode({'sample_rate': 16000}));

      _channel!.stream.listen(
        _onDataReceived, 
        onError: _onError, 
        onDone: _onDone,
        cancelOnError: false,
      );
    } catch (e) {
      _onError(e);
    } finally {
      _isConnecting = false;
    }
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
    _scheduleReconnect();
  }

  void _onDone() {
    print('WebSocket closed');
    _scheduleReconnect();
  }

  void _scheduleReconnect() {
    if (_reconnectTimer?.isActive ?? false) return;
    print('Reconnecting to Audio Subsystem in 3 seconds...');
    _reconnectTimer = Timer(const Duration(seconds: 3), () {
      connect();
    });
  }

  void streamAudio(Float32List audioBytes) {
    if (_channel != null && _channel!.closeCode == null) {
      _channel!.sink.add(audioBytes.buffer.asUint8List());
    }
  }

  void disconnect() {
    _reconnectTimer?.cancel();
    _channel?.sink.close();
  }

  void dispose() {
    disconnect();
    _deepfakeStreamController.close();
  }
}
