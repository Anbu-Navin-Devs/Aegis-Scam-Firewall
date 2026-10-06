package com.aegis.scamfirewall.core.ml

import java.util.regex.Pattern

data class LocalScamResult(
    val isScam: Boolean,
    val scamScore: Int, // 0 to 100
    val reason: String,
    val detectedTriggers: List<String>
)

/**
 * On-Device High-Speed Scam Classifier (Tier-1 Local Model).
 *
 * Runs locally in under 2ms without requiring internet connection or cloud API calls.
 * Evaluates text against multi-factor social engineering and fraud indicators:
 * 1. Suspicious/Obfuscated Link Detection (IP addresses, URL shorteners, fake domains)
 * 2. High-Pressure Urgency Tactics
 * 3. Authority & Brand Impersonation (Banks, Couriers, IRS, Tech Support)
 * 4. Financial Demands (Gift cards, Crypto, Wire transfers)
 * 5. Credential & OTP Harvesting
 * 6. Deceptive Lottery & Inheritance Lures
 */
object LocalScamClassifier {

    // --- Regular Expressions for Phishing Links ---
    private val IP_URL_PATTERN = Pattern.compile(
        "https?://(?:\\d{1,3}\\.){3}\\d{1,3}(?::\\d+)?(?:/[^\\s]*)?",
        Pattern.CASE_INSENSITIVE
    )

    private val SHORTENER_URL_PATTERN = Pattern.compile(
        "https?://(?:bit\\.ly|tinyurl\\.com|t\\.co|is\\.gd|cutt\\.ly|rb\\.gy|ow\\.ly|buff\\.ly|rebrand\\.ly|shorte\\.st|adf\\.ly)/[^\\s]*",
        Pattern.CASE_INSENSITIVE
    )

    private val SUSPICIOUS_DOMAIN_PATTERN = Pattern.compile(
        "https?://[^\\s]*(?:secure-[a-z0-9]+|login-[a-z0-9]+|verify-[a-z0-9]+|account-[a-z0-9]+|update-[a-z0-9]+|support-[a-z0-9]+)\\.[a-z]{2,}",
        Pattern.CASE_INSENSITIVE
    )

    private val SUSPICIOUS_TLD_PATTERN = Pattern.compile(
        "https?://[^\\s]+\\.(?:xyz|top|work|icu|buzz|cam|tk|cf|ga|gq|ml|pw|bid|loan|win)(?:/[^\\s]*)?",
        Pattern.CASE_INSENSITIVE
    )

    // --- Keyword Matrix Categories ---

    private val URGENCY_TRIGGERS = listOf(
        "immediate action required", "immediately", "urgent", "within 24 hours", "within 12 hours",
        "account suspended", "suspended permanently", "arrest warrant", "legal action",
        "law enforcement", "warrant issued", "final notice", "failure to respond",
        "act now", "limited time", "time-sensitive", "police notice", "court summons"
    )

    private val IMPERSONATION_TRIGGERS = listOf(
        "irs", "internal revenue service", "social security administration", "ssa",
        "bank of america", "wells fargo", "chase bank", "citibank", "capital one",
        "paypal", "venmo", "zelle", "cashapp",
        "usps", "fedex", "dhl express", "ups package", "postal service",
        "apple security", "microsoft support", "amazon order", "netflix billing",
        "geek squad", "border patrol", "customs department"
    )

    private val FINANCIAL_DEMAND_TRIGGERS = listOf(
        "gift card", "apple gift card", "google play card", "target card",
        "bitcoin", "cryptocurrency", "btc wallet", "wire transfer", "western union",
        "moneygram", "unpaid invoice", "overdue toll", "toll violation",
        "pay immediately to avoid", "settlement fee", "refundable deposit"
    )

    private val HARVESTING_TRIGGERS = listOf(
        "one-time password", "otp code", "otp", "verification code", "security code",
        "enter your pin", "confirm your password", "verify your ssn", "social security number",
        "billing info", "card details", "cvv", "click here to login", "unlock your account",
        "verify identity"
    )

    private val PRIZE_LURE_TRIGGERS = listOf(
        "congratulations you won", "claim your prize", "lucky winner", "you have been selected",
        "cash reward", "lottery prize", "inheritance fund", "sweepstakes", "unclaimed funds",
        "free voucher", "exclusive gift"
    )

    fun classify(text: String): LocalScamResult {
        val lower = text.lowercase()
        var score = 0
        val detected = mutableListOf<String>()

        // 1. Check Links & URLs (Weight: 25 - 40 pts)
        if (IP_URL_PATTERN.matcher(text).find()) {
            score += 40
            detected.add("Suspicious raw IP address link detected")
        }
        if (SHORTENER_URL_PATTERN.matcher(text).find()) {
            score += 25
            detected.add("Obfuscated shortlink detected (URL shortener)")
        }
        if (SUSPICIOUS_DOMAIN_PATTERN.matcher(text).find()) {
            score += 35
            detected.add("Deceptive fake-login / verification domain detected")
        }
        if (SUSPICIOUS_TLD_PATTERN.matcher(text).find()) {
            score += 25
            detected.add("High-risk phishing domain extension detected")
        }

        // 2. Check Urgency / Intimidation (Weight: 15 - 30 pts)
        val matchedUrgency = URGENCY_TRIGGERS.filter { lower.contains(it) }
        if (matchedUrgency.isNotEmpty()) {
            val pts = minOf(30, matchedUrgency.size * 15)
            score += pts
            detected.add("High-pressure urgency tactics: ${matchedUrgency.take(2).joinToString(", ")}")
        }

        // 3. Check Authority / Brand Impersonation (Weight: 15 - 30 pts)
        val matchedImpersonation = IMPERSONATION_TRIGGERS.filter { lower.contains(it) }
        if (matchedImpersonation.isNotEmpty()) {
            val pts = minOf(30, matchedImpersonation.size * 15)
            score += pts
            detected.add("Brand / Government impersonation: ${matchedImpersonation.take(2).joinToString(", ")}")
        }

        // 4. Check Financial Demands (Weight: 25 - 35 pts)
        val matchedFinance = FINANCIAL_DEMAND_TRIGGERS.filter { lower.contains(it) }
        if (matchedFinance.isNotEmpty()) {
            val pts = minOf(35, matchedFinance.size * 20)
            score += pts
            detected.add("Untraceable payment or debt demand: ${matchedFinance.take(2).joinToString(", ")}")
        }

        // 5. Check Credential & OTP Harvesting (Weight: 25 - 40 pts)
        val matchedHarvest = HARVESTING_TRIGGERS.filter { lower.contains(it) }
        if (matchedHarvest.isNotEmpty()) {
            val pts = minOf(40, matchedHarvest.size * 20)
            score += pts
            detected.add("Credential / OTP harvesting attempt: ${matchedHarvest.take(2).joinToString(", ")}")
        }

        // 6. Check Prize / Lottery Lures (Weight: 20 - 30 pts)
        val matchedPrize = PRIZE_LURE_TRIGGERS.filter { lower.contains(it) }
        if (matchedPrize.isNotEmpty()) {
            val pts = minOf(30, matchedPrize.size * 15)
            score += pts
            detected.add("Unsolicited prize / lottery lure: ${matchedPrize.take(2).joinToString(", ")}")
        }

        // Bound score 0 to 100
        val finalScore = minOf(100, score)
        val isScam = finalScore >= 50

        val reasonSummary = if (detected.isNotEmpty()) {
            detected.joinToString("; ")
        } else {
            "No known malicious social engineering or fraud indicators found."
        }

        return LocalScamResult(
            isScam = isScam,
            scamScore = finalScore,
            reason = reasonSummary,
            detectedTriggers = detected
        )
    }
}
