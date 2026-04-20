import 'package:freezed_annotation/freezed_annotation.dart';

part 'intent_response.freezed.dart';
part 'intent_response.g.dart';

@freezed
class IntentResponse with _$IntentResponse {
  const factory IntentResponse({
    @JsonKey(name: 'is_scam') required bool isScam,
    @JsonKey(name: 'scam_score') required int scamScore,
    required String reason,
  }) = _IntentResponse;

  factory IntentResponse.fromJson(Map<String, dynamic> json) =>
      _$IntentResponseFromJson(json);
}
