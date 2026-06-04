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
    final isSynthetic = json['is_synthetic'] as bool? ?? json['is_deepfake'] as bool? ?? false;
    
    double confidence = (json['confidence_score'] ?? 0.0).toDouble();
    if (confidence > 1.0) {
      confidence = confidence / 100.0;
    }

    final List<String> flags = [];
    if (json['flags'] != null) {
      flags.addAll(List<String>.from(json['flags']));
    } else if (json['analysis_details'] != null) {
      final details = json['analysis_details'] as String;
      if (details.contains('|')) {
        flags.addAll(details.split('|').map((s) => s.trim()).where((s) => s.isNotEmpty));
      } else {
        flags.add(details);
      }
    }

    return DeepfakeResponse(
      timestamp: json['timestamp'] as String? ?? DateTime.now().toIso8601String(),
      isSynthetic: isSynthetic,
      confidenceScore: confidence,
      flags: flags,
    );
  }
}
