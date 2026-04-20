class ThreatLog {
  final String id;
  final String timestamp;
  final String threatType;
  final String details;

  ThreatLog({
    required this.id,
    required this.timestamp,
    required this.threatType,
    required this.details,
  });

  factory ThreatLog.fromJson(Map<String, dynamic> json) {
    return ThreatLog(
      id: json['id'] as String? ?? 'Unknown',
      timestamp: json['timestamp'] as String? ?? 'Unknown',
      threatType: json['threat_type'] as String? ?? 'Unknown',
      details: json['details'] as String? ?? 'No details',
    );
  }
}
