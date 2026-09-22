package ua.mil.cyberguard

import android.graphics.drawable.Drawable

enum class ThreatSeverity {
    CRITICAL,
    WARNING,
    SAFE
}

data class SuspiciousApp(
    val appName: String,
    val packageName: String,
    val icon: Drawable?,
    val isSideloaded: Boolean,
    val hasAccessibility: Boolean,
    val hasBackgroundLocation: Boolean,
    val reasons: List<String>,
    val severity: ThreatSeverity
)

data class AuditReport(
    val deviceModel: String,
    val androidVersion: String,
    val scanTimestamp: String,
    val totalAppsScanned: Int,
    val sideloadedAppsCount: Int,
    val threatsFound: List<SuspiciousApp>,
    val isSafe: Boolean,
    val isRooted: Boolean,
    val isUsbDebuggingEnabled: Boolean
)
