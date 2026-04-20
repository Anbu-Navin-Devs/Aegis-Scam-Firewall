class DeepfakeResponse {
  final String timestamp;
  final bool isSynthetic;
  final double confidenceScore;
  final List<String> flags;

  DeepfakeResponse({
    required this.timestamp,
    required this.isSynthetic,
    required this.confidenceScore,
    required this.flags,
  });

  factory DeepfakeResponse.fromJson(Map<String, dynamic> json) {
    return DeepfakeResponse(
      timestamp: json['timestamp'] as String? ?? 'Unknown',
      isSynthetic: json['is_synthetic'] as bool? ?? false,
      confidenceScore: (json['confidence_score'] ?? 0.0).toDouble(),
      flags: List<String>.from(json['flags'] ?? []),
    );
  }
}
