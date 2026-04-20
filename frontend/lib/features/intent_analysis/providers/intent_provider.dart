import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_service.dart';
import '../../models/intent_response.dart';

// Provides a singleton of ApiService
final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});

// A FutureProvider family to analyze intent dynamically
final intentAnalysisProvider = FutureProvider.family<IntentResponse, String>((ref, transcript) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.analyzeIntent(transcript);
});
