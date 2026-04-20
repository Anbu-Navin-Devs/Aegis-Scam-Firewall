class DocumentScanResponse {
  final String riskLevel;
  final List<String> flaggedClauses;
  final String summary;

  DocumentScanResponse({
    required this.riskLevel,
    required this.flaggedClauses,
    required this.summary,
  });

  factory DocumentScanResponse.fromJson(Map<String, dynamic> json) {
    return DocumentScanResponse(
      riskLevel: json['risk_level'] as String? ?? 'Unknown',
      flaggedClauses: List<String>.from(json['flagged_clauses'] ?? []),
      summary: json['summary'] as String? ?? 'No summary provided',
    );
  }
}
