package com.aegis.scamfirewall.models

import com.google.gson.annotations.SerializedName

data class IntentResponse(
    @SerializedName("is_scam") val isScam: Boolean,
    @SerializedName("scam_score") val scamScore: Int,
    @SerializedName("reason") val reason: String
)
