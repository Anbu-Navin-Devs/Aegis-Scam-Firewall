import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_provider.dart';
import '../../../models/threat_log.dart';

final historyProvider = FutureProvider.autoDispose<List<ThreatLog>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getHistoryLogs(limit: 20);
});
