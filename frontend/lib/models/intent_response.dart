class IntentResponse {
  final bool isScam;
  final int scamScore;
  final String reason;

  IntentResponse({
    required this.isScam,
    required this.scamScore,
    required this.reason,
  });

  factory IntentResponse.fromJson(Map<String, dynamic> json) {
    return IntentResponse(
      isScam: json['is_scam'] as bool? ?? false,
      scamScore: json['scam_score'] as int? ?? 0,
      reason: json['reason'] as String? ?? '',
    );
  }
}
