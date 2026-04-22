class ThreatLog {
  final String id;
  final String timestamp;
  final String moduleType;
  final String riskLevel;
  final Map<String, dynamic> detailsJson;

  ThreatLog({
    required this.id,
    required this.timestamp,
    required this.moduleType,
    required this.riskLevel,
    required this.detailsJson,
  });

  factory ThreatLog.fromJson(Map<String, dynamic> json) {
    return ThreatLog(
      id: json['id'] as String? ?? 'Unknown',
      timestamp: json['timestamp'] as String? ?? 'Unknown',
      moduleType: json['module_type'] as String? ?? 'Unknown',
      riskLevel: json['risk_level'] as String? ?? 'Unknown',
      detailsJson: json['details_json'] as Map<String, dynamic>? ?? {},
    );
  }
}
