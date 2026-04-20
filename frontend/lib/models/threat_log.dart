import 'package:freezed_annotation/freezed_annotation.dart';

part 'threat_log.freezed.dart';
part 'threat_log.g.dart';

@freezed
class ThreatLog with _$ThreatLog {
  const factory ThreatLog({
    required String id,
    required String timestamp,
    @JsonKey(name: 'threat_type') required String threatType,
    required String details,
  }) = _ThreatLog;

  factory ThreatLog.fromJson(Map<String, dynamic> json) =>
      _$ThreatLogFromJson(json);
}
