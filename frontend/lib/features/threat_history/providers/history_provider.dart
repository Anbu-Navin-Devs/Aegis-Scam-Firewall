import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_provider.dart';
import '../../../models/threat_log.dart';

final historyProvider = FutureProvider.autoDispose<List<ThreatLog>>((ref) async {
  // Simulate network delay
  await Future.delayed(const Duration(seconds: 1));

  return [
    ThreatLog(
      id: '1',
      timestamp: DateTime.now().toIso8601String(),
      moduleType: 'intent',
      riskLevel: 'SCAM_DETECTED',
      detailsJson: {
        "is_scam": true,
        "scam_score": 96,
        "reason": "IRS Impersonation: Caller demanded immediate payment via gift cards."
      },
    ),
    ThreatLog(
      id: '2',
      timestamp: DateTime.now().subtract(const Duration(minutes: 15)).toIso8601String(),
      moduleType: 'document',
      riskLevel: 'CRITICAL',
      detailsJson: {
        "summary": "Hidden auto-renewal clause found.",
        "flagged_clauses": [
          "Section 4.2: Auto-renewal hidden in fine print."
        ]
      },
    ),
    ThreatLog(
      id: '3',
      timestamp: DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
      moduleType: 'audio',
      riskLevel: 'DEEPFAKE_DETECTED',
      detailsJson: {
        "is_deepfake": true,
        "confidence_score": 88.5,
        "analysis_details": "Spectral flatness is abnormally uniform."
      },
    ),
  ];
});
