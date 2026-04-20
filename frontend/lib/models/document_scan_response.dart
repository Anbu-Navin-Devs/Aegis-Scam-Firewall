import 'package:freezed_annotation/freezed_annotation.dart';

part 'document_scan_response.freezed.dart';
part 'document_scan_response.g.dart';

@freezed
class DocumentScanResponse with _$DocumentScanResponse {
  const factory DocumentScanResponse({
    @JsonKey(name: 'risk_level') required String riskLevel,
    @JsonKey(name: 'flagged_clauses') required List<String> flaggedClauses,
    required String summary,
  }) = _DocumentScanResponse;

  factory DocumentScanResponse.fromJson(Map<String, dynamic> json) =>
      _$DocumentScanResponseFromJson(json);
}
