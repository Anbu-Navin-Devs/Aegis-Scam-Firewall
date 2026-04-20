import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_provider.dart';
import '../../../core/network/api_service.dart';
import '../../../models/intent_response.dart';

final intentProvider = StateNotifierProvider<IntentNotifier, AsyncValue<IntentResponse?>>((ref) {
  return IntentNotifier(ref.watch(apiServiceProvider));
});

class IntentNotifier extends StateNotifier<AsyncValue<IntentResponse?>> {
  final ApiService _apiService;
  
  IntentNotifier(this._apiService) : super(const AsyncData(null));

  Future<void> analyzeIntent(String transcript) async {
    if (transcript.trim().isEmpty) return;
    
    state = const AsyncLoading();
    try {
      final response = await _apiService.analyzeIntent(transcript);
      state = AsyncData(response);
    } catch (e, stackTrace) {
      state = AsyncError(e, stackTrace);
    }
  }

  void reset() {
    state = const AsyncData(null);
  }
}
