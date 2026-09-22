package ua.mil.cyberguard

import android.content.Context
import android.content.pm.ApplicationInfo
import android.content.pm.PackageInfo
import android.content.pm.PackageManager
import android.os.Build
import android.provider.Settings
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class SecurityAuditEngine(private val context: Context) {

    private val pm: PackageManager = context.packageManager

    // Довірені пакети (офіційні месенджери та штабне військове ПЗ)
    private val trustedPackages = setOf(
        "org.telegram.messenger",
        "org.telegram.plus",
        "org.thoughtcrime.securesms", // Signal
        "com.whatsapp",
        "com.google.android.apps.maps",
        "com.mapswithme.maps.pro",
        "ua.gov.army.app", // Армія+
        "com.android.vending", // Play Store
        "com.google.android.gms",
        "ua.mil.cyberguard"
    )

    fun performAudit(): AuditReport {
        val installedPackages = pm.getInstalledPackages(PackageManager.GET_PERMISSIONS or PackageManager.GET_SERVICES)
        val threats = mutableListOf<SuspiciousApp>()
        var sideloadedCount = 0
        var totalScanned = 0

        for (pkg in installedPackages) {
            // Пропускаємо системні додатки вендора, якщо вони не оновлювалися користувачем
            val isSystem = (pkg.applicationInfo.flags and ApplicationInfo.FLAG_SYSTEM) != 0
            val isUpdatedSystem = (pkg.applicationInfo.flags and ApplicationInfo.FLAG_UPDATED_SYSTEM_APP) != 0
            
            if (isSystem && !isUpdatedSystem) {
                continue
            }

            val pkgName = pkg.packageName
            if (trustedPackages.contains(pkgName)) {
                continue
            }

            totalScanned++

            val appName = pkg.applicationInfo.loadLabel(pm).toString()
            val icon = pkg.applicationInfo.loadIcon(pm)
            val isSideloaded = checkIsSideloaded(pkgName)
            if (isSideloaded) {
                sideloadedCount++
            }

            val requestedPerms = pkg.requestedPermissions ?: emptyArray()

            // 1. Служба доступності (Accessibility) — критичний маркер RAT
            val hasAccessibility = hasAccessibilityService(pkg)
            
            // 2. Фонова геолокація (Background Location)
            val hasBgLocation = requestedPerms.contains("android.permission.ACCESS_BACKGROUND_LOCATION")
            
            // 3. Інші чутливі дозволи
            val hasAlertWindow = requestedPerms.contains("android.permission.SYSTEM_ALERT_WINDOW")
            val hasAudio = requestedPerms.contains("android.permission.RECORD_AUDIO")
            val hasSms = requestedPerms.contains("android.permission.READ_SMS") or requestedPerms.contains("android.permission.RECEIVE_SMS")

            val reasons = mutableListOf<String>()

            if (hasAccessibility) {
                reasons.add("🚨 Служба доступності (читання екрану / клавіатури)")
            }
            if (hasBgLocation) {
                reasons.add("📍 Фоновий GPS (збір координат при вимкненому екрані)")
            }
            if (isSideloaded) {
                reasons.add("📦 Встановлено з невідомого джерела (чат/браузер)")
            }
            if (hasAlertWindow && isSideloaded) {
                reasons.add("⚠️ Малювання вікон поверх інших програм (фішинг)")
            }
            if ((hasAudio || hasSms) && isSideloaded) {
                reasons.add("🎙️ Доступ до мікрофону / перехоплення SMS")
            }

            // Визначаємо рівень загрози
            if (hasAccessibility || (hasBgLocation && isSideloaded)) {
                threats.add(
                    SuspiciousApp(
                        appName = appName,
                        packageName = pkgName,
                        icon = icon,
                        isSideloaded = isSideloaded,
                        hasAccessibility = hasAccessibility,
                        hasBackgroundLocation = hasBgLocation,
                        reasons = reasons,
                        severity = ThreatSeverity.CRITICAL
                    )
                )
            } else if (reasons.size >= 2 || (isSideloaded && (hasAudio || hasSms))) {
                threats.add(
                    SuspiciousApp(
                        appName = appName,
                        packageName = pkgName,
                        icon = icon,
                        isSideloaded = isSideloaded,
                        hasAccessibility = false,
                        hasBackgroundLocation = hasBgLocation,
                        reasons = reasons,
                        severity = ThreatSeverity.WARNING
                    )
                )
            }
        }

        val isRooted = checkRoot()
        val isAdb = checkUsbDebugging()

        val timestamp = SimpleDateFormat("dd.MM.yyyy HH:mm", Locale.getDefault()).format(Date())

        return AuditReport(
            deviceModel = "${Build.MANUFACTURER} ${Build.MODEL}",
            androidVersion = "Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})",
            scanTimestamp = timestamp,
            totalAppsScanned = totalScanned,
            sideloadedAppsCount = sideloadedCount,
            threatsFound = threats,
            isSafe = threats.isEmpty(),
            isRooted = isRooted,
            isUsbDebuggingEnabled = isAdb
        )
    }

    private fun checkIsSideloaded(packageName: String): Boolean {
        return try {
            val installer = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                pm.getInstallSourceInfo(packageName).installingPackageName
            } else {
                @Suppress("DEPRECATION")
                pm.getInstallerPackageName(packageName)
            }
            // Якщо інсталятор порожній або це браузер/телеграм — це sideload
            installer == null || installer.contains("telegram") || installer.contains("chrome") || 
                    installer.contains("browser") || installer.contains("download") || installer.contains("whatsapp")
        } catch (e: Exception) {
            false
        }
    }

    private fun hasAccessibilityService(pkg: PackageInfo): Boolean {
        val services = pkg.services ?: return false
        for (service in services) {
            if (service.permission == "android.permission.BIND_ACCESSIBILITY_SERVICE") {
                return true
            }
        }
        return false
    }

    private fun checkRoot(): Boolean {
        val paths = arrayOf(
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su"
        )
        for (path in paths) {
            if (File(path).exists()) return true
        }
        return false
    }

    private fun checkUsbDebugging(): Boolean {
        return try {
            Settings.Global.getInt(context.contentResolver, Settings.Global.ADB_ENABLED, 0) == 1
        } catch (e: Exception) {
            false
        }
    }
}
