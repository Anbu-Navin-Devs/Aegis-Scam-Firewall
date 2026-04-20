import 'package:freezed_annotation/freezed_annotation.dart';

part 'deepfake_response.freezed.dart';
part 'deepfake_response.g.dart';

@freezed
class DeepfakeResponse with _$DeepfakeResponse {
  const factory DeepfakeResponse({
    required String timestamp,
    @JsonKey(name: 'is_synthetic') required bool isSynthetic,
    @JsonKey(name: 'confidence_score') required double confidenceScore,
    required List<String> flags,
  }) = _DeepfakeResponse;

  factory DeepfakeResponse.fromJson(Map<String, dynamic> json) =>
      _$DeepfakeResponseFromJson(json);
}
