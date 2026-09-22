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

    // Довірені пакети (офіційні месенджери, навігація та штабне військове ПЗ)
    private val trustedPackages = setOf(
        "org.telegram.messenger",
        "org.telegram.plus",
        "org.thoughtcrime.securesms", // Signal
        "com.whatsapp",
        "com.viber.voip",
        "com.google.android.apps.maps",
        "com.mapswithme.maps.pro",
        "ua.gov.army.app", // Армія+
        "ua.mil.delta", // Дельта
        "ua.kropyva", // Кропива
        "com.android.vending", // Play Store
        "com.google.android.gms",
        "ua.mil.cyberguard"
    )

    // Префікси системних компонентів та фабричних вендорів смартфонів (OnePlus, Samsung, Xiaomi тощо)
    private val vendorPrefixes = listOf(
        "com.oneplus.",
        "com.coloros.",
        "com.oppo.",
        "com.oplus.",
        "com.heytap.",
        "com.samsung.",
        "com.sec.android.",
        "com.miui.",
        "com.xiaomi.",
        "com.huawei.",
        "com.google.android.",
        "com.android.",
        "com.qualcomm.",
        "com.mediatek.",
        "com.lge."
    )

    // Офіційні магазини додатків (додатки з них не є sideloaded з чатів/apk)
    private val officialStorePrefixes = listOf(
        "com.android.vending",
        "com.google.android.feedback",
        "com.heytap.market",
        "com.oppo.market",
        "com.oneplus.market",
        "com.sec.android.app.samsungapps",
        "com.xiaomi.market",
        "com.miui.market",
        "com.huawei.appmarket",
        "com.amazon.venezia"
    )

    fun performAudit(): AuditReport {
        val installedPackages = pm.getInstalledPackages(PackageManager.GET_PERMISSIONS or PackageManager.GET_SERVICES)
        val threats = mutableListOf<SuspiciousApp>()
        var sideloadedCount = 0
        var totalScanned = 0

        for (pkg in installedPackages) {
            val pkgName = pkg.packageName

            // 1. Пропускаємо штатно довірені додатки
            if (trustedPackages.contains(pkgName)) {
                continue
            }

            val appInfo = pkg.applicationInfo ?: continue
            val isSystem = (appInfo.flags and ApplicationInfo.FLAG_SYSTEM) != 0
            val isUpdatedSystem = (appInfo.flags and ApplicationInfo.FLAG_UPDATED_SYSTEM_APP) != 0
            val isVendor = isVendorPackage(pkgName)

            // Служба доступності (Accessibility)
            val hasAccessibility = hasAccessibilityService(pkg)

            // Якщо це системний або фабричний вендорський додаток без сторонньої служби доступності — пропускаємо
            if ((isSystem || isUpdatedSystem || isVendor) && !hasAccessibility) {
                continue
            }

            totalScanned++

            val appName = appInfo.loadLabel(pm).toString()
            val icon = appInfo.loadIcon(pm)
            val installer = getInstallerPackage(pkgName)
            val isFromOfficialStore = isFromOfficialStore(installer)

            // Якщо системний/вендорський або з офіційного маркету — це НЕ sideload
            val isSideloaded = if (isSystem || isUpdatedSystem || isVendor || isFromOfficialStore) {
                false
            } else {
                checkIsSideloaded(installer)
            }

            if (isSideloaded) {
                sideloadedCount++
            }

            val requestedPerms = pkg.requestedPermissions ?: emptyArray()

            // Фонова геолокація
            val hasBgLocation = requestedPerms.contains("android.permission.ACCESS_BACKGROUND_LOCATION")

            // Інші чутливі дозволи
            val hasAlertWindow = requestedPerms.contains("android.permission.SYSTEM_ALERT_WINDOW")
            val hasAudio = requestedPerms.contains("android.permission.RECORD_AUDIO")
            val hasSms = requestedPerms.contains("android.permission.READ_SMS") || requestedPerms.contains("android.permission.RECEIVE_SMS")

            val reasons = mutableListOf<String>()

            if (hasAccessibility) {
                reasons.add("🚨 Служба доступності (читання екрану / клавіатури)")
            }
            if (hasBgLocation) {
                reasons.add("📍 Фоновий GPS (збір координат при вимкненому екрані)")
            }
            if (isSideloaded) {
                reasons.add("📦 Встановлено не з Play Store (з чату або браузера)")
            }
            if (hasAlertWindow && isSideloaded) {
                reasons.add("⚠️ Малювання вікон поверх інших програм (фішинг)")
            }
            if ((hasAudio || hasSms) && isSideloaded) {
                reasons.add("🎙️ Доступ до мікрофону / перехоплення SMS")
            }

            // Класифікація загрози
            if (hasAccessibility && isSideloaded) {
                // Найнебезпечніше: сторонній APK з доступом до Accessibility
                threats.add(
                    SuspiciousApp(
                        appName = appName,
                        packageName = pkgName,
                        icon = icon,
                        isSideloaded = true,
                        hasAccessibility = true,
                        hasBackgroundLocation = hasBgLocation,
                        reasons = reasons,
                        severity = ThreatSeverity.CRITICAL
                    )
                )
            } else if (hasAccessibility) {
                // Додаток з маркету (наприклад ChatGPT, LG ThinQ), що зареєстрував Accessibility
                threats.add(
                    SuspiciousApp(
                        appName = appName,
                        packageName = pkgName,
                        icon = icon,
                        isSideloaded = false,
                        hasAccessibility = true,
                        hasBackgroundLocation = hasBgLocation,
                        reasons = reasons,
                        severity = ThreatSeverity.WARNING
                    )
                )
            } else if (isSideloaded && (hasBgLocation || hasAlertWindow || hasAudio || hasSms)) {
                // Sideloaded APK з небезпечними дозволами
                threats.add(
                    SuspiciousApp(
                        appName = appName,
                        packageName = pkgName,
                        icon = icon,
                        isSideloaded = true,
                        hasAccessibility = false,
                        hasBackgroundLocation = hasBgLocation,
                        reasons = reasons,
                        severity = ThreatSeverity.CRITICAL
                    )
                )
            } else if (isSideloaded && reasons.size >= 2) {
                threats.add(
                    SuspiciousApp(
                        appName = appName,
                        packageName = pkgName,
                        icon = icon,
                        isSideloaded = true,
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

    private fun isVendorPackage(packageName: String): Boolean {
        return vendorPrefixes.any { packageName.startsWith(it) }
    }

    private fun isFromOfficialStore(installer: String?): Boolean {
        if (installer == null) return false
        return officialStorePrefixes.any { installer.startsWith(it) }
    }

    private fun getInstallerPackage(packageName: String): String? {
        return try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                pm.getInstallSourceInfo(packageName).installingPackageName
            } else {
                @Suppress("DEPRECATION")
                pm.getInstallerPackageName(packageName)
            }
        } catch (e: Exception) {
            null
        }
    }

    private fun checkIsSideloaded(installer: String?): Boolean {
        if (installer == null) return true
        val suspiciousSources = listOf("telegram", "chrome", "browser", "download", "whatsapp", "packageinstaller")
        return suspiciousSources.any { installer.contains(it, ignoreCase = true) }
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
