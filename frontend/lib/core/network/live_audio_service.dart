import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../models/deepfake_response.dart';
import '../config/app_config.dart';

class LiveAudioService {
  final _deepfakeStreamController = StreamController<DeepfakeResponse>.broadcast();
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  bool _isConnected = false;

  Stream<DeepfakeResponse> get threatStream => _deepfakeStreamController.stream;

  void connect() {
    disconnect();
    
    final uri = Uri.parse('${AppConfig.wsUrl}/api/v1/live-audio/stream');
    try {
      _channel = WebSocketChannel.connect(uri);
      _isConnected = true;

      // 1. Send handshake frame
      final handshake = {
        'sample_rate': 16000,
        'channels': 1,
      };
      _channel!.sink.add(jsonEncode(handshake));

      // 2. Listen to backend evaluations
      _subscription = _channel!.stream.listen(
        (message) {
          try {
            final data = jsonDecode(message as String);
            if (data['event'] == 'handshake_ok') {
              return;
            }
            if (data['event'] == 'error') {
              return;
            }
            if (data['event'] == 'session_end') {
              disconnect();
              return;
            }
            
            final response = DeepfakeResponse.fromJson(data);
            if (!_deepfakeStreamController.isClosed) {
              _deepfakeStreamController.add(response);
            }
          } catch (_) {}
        },
        onError: (error) {
          _isConnected = false;
          if (!_deepfakeStreamController.isClosed) {
            _deepfakeStreamController.addError(error);
          }
        },
        onDone: () {
          _isConnected = false;
        },
      );
    } catch (e) {
      _isConnected = false;
      if (!_deepfakeStreamController.isClosed) {
        _deepfakeStreamController.addError(e);
      }
    }
  }

  void streamAudio(Float32List audioBytes) {
    if (_isConnected && _channel != null) {
      final bytes = audioBytes.buffer.asUint8List(
        audioBytes.offsetInBytes,
        audioBytes.lengthInBytes,
      );
      _channel!.sink.add(bytes);
    }
  }

  void disconnect() {
    if (_isConnected && _channel != null) {
      try {
        _channel!.sink.add('STOP');
      } catch (_) {}
    }
    _subscription?.cancel();
    _subscription = null;
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
  }

  void dispose() {
    disconnect();
    _deepfakeStreamController.close();
  }
}
