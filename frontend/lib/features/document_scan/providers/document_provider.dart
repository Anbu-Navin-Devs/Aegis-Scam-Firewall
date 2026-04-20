import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_provider.dart';
import '../../../core/network/api_service.dart';
import '../../../models/document_scan_response.dart';

final documentProvider = StateNotifierProvider<DocumentNotifier, AsyncValue<DocumentScanResponse?>>((ref) {
  return DocumentNotifier(ref.watch(apiServiceProvider));
});

class DocumentNotifier extends StateNotifier<AsyncValue<DocumentScanResponse?>> {
  final ApiService _apiService;

  DocumentNotifier(this._apiService) : super(const AsyncData(null));

  Future<void> scanDocument(String filePath) async {
    state = const AsyncLoading();
    try {
      final response = await _apiService.scanDocument(filePath);
      state = AsyncData(response);
    } catch (e, stackTrace) {
      state = AsyncError(e, stackTrace);
    }
  }

  void reset() {
    state = const AsyncData(null);
  }
}
