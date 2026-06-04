package com.aegis.scamfirewall.models

import com.google.gson.annotations.SerializedName

data class DeepfakeResponse(
    @SerializedName("is_deepfake") val isSynthetic: Boolean,
    @SerializedName("confidence_score") val rawConfidenceScore: Float,
    @SerializedName("analysis_details") val rawDetails: String?
) {
    // Normalised confidence score between 0.0 and 1.0
    val confidenceScore: Float
        get() = if (rawConfidenceScore > 1.0f) rawConfidenceScore / 100.0f else rawConfidenceScore

    val flags: List<String>
        get() = rawDetails?.split("|")?.map { it.trim() }?.filter { it.contains("TTS") || it.contains("synthetic") || it.contains("vocoder") } ?: emptyList()
}
