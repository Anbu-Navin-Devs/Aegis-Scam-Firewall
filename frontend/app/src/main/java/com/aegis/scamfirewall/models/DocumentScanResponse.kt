package com.aegis.scamfirewall.models

import com.google.gson.annotations.SerializedName

data class DocumentScanResponse(
    @SerializedName("risk_level") val riskLevel: String,
    @SerializedName("flagged_clauses") val flaggedClauses: List<String>,
    @SerializedName("summary") val summary: String
)
