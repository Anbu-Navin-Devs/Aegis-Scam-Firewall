package com.aegis.scamfirewall.models

import com.google.gson.annotations.SerializedName

data class ThreatLog(
    @SerializedName("id") val id: String,
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("module_type") val moduleType: String,
    @SerializedName("risk_level") val riskLevel: String,
    @SerializedName("details_json") val detailsJson: Map<String, Any>
)
