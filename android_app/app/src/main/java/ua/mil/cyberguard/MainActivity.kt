package ua.mil.cyberguard

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import ua.mil.cyberguard.databinding.ActivityMainBinding
import ua.mil.cyberguard.utils.DeepLinkHelper

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var auditEngine: SecurityAuditEngine
    private var lastReport: AuditReport? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        auditEngine = SecurityAuditEngine(this)

        setupListeners()
    }

    private fun setupListeners() {
        binding.btnScan.setOnClickListener {
            startAudit()
        }

        binding.btnActionTg.setOnClickListener {
            DeepLinkHelper.openTelegramDevices(this)
        }

        binding.btnActionCamera.setOnClickListener {
            DeepLinkHelper.openApplicationSettings(this)
        }

        binding.btnCopyReport.setOnClickListener {
            copyReportToClipboard()
        }
    }

    private fun startAudit() {
        binding.btnScan.isEnabled = false
        binding.btnScan.text = getString(R.string.btn_scanning)
        binding.progressBar.visibility = View.VISIBLE

        lifecycleScope.launch(Dispatchers.Default) {
            val report = auditEngine.performAudit()

            withContext(Dispatchers.Main) {
                lastReport = report
                renderReport(report)
            }
        }
    }

    private fun renderReport(report: AuditReport) {
        binding.progressBar.visibility = View.GONE
        binding.btnScan.isEnabled = true
        binding.btnScan.text = getString(R.string.btn_scan)

        // Show statistics counters
        binding.layoutStats.visibility = View.VISIBLE
        binding.tvStatTotal.text = report.totalAppsScanned.toString()
        binding.tvStatSideloaded.text = report.sideloadedAppsCount.toString()
        binding.tvStatThreats.text = report.threatsFound.size.toString()

        binding.btnCopyReport.visibility = View.VISIBLE

        if (report.isSafe) {
            // SAFE STATE
            binding.cardStatus.strokeColor = ContextCompat.getColor(this, R.color.cyber_green)
            binding.tvStatusIcon.text = "🟢"
            binding.tvStatusTitle.text = getString(R.string.status_safe_title)
            binding.tvStatusTitle.setTextColor(ContextCompat.getColor(this, R.color.cyber_green))
            binding.tvStatusDesc.text = getString(R.string.status_safe_desc)

            binding.tvThreatsHeader.visibility = View.GONE
            binding.rvThreats.visibility = View.GONE
        } else {
            // THREATS DETECTED
            binding.cardStatus.strokeColor = ContextCompat.getColor(this, R.color.cyber_red)
            binding.tvStatusIcon.text = "🔴"
            binding.tvStatusTitle.text = getString(R.string.status_threat_title)
            binding.tvStatusTitle.setTextColor(ContextCompat.getColor(this, R.color.cyber_red))
            binding.tvStatusDesc.text = "Виявлено ${report.threatsFound.size} підозрілих програм з доступом до екрану, клавіатури або фонового GPS!"

            binding.tvThreatsHeader.visibility = View.VISIBLE
            binding.rvThreats.visibility = View.VISIBLE
            binding.rvThreats.layoutManager = LinearLayoutManager(this)
            binding.rvThreats.adapter = ThreatAdapter(report.threatsFound)
        }
    }

    private fun copyReportToClipboard() {
        val report = lastReport ?: return
        val statusText = if (report.isSafe) "🟢 БЕЗПЕЧНО" else "🔴 ВИЯВЛЕНО ЗАГРОЗИ (${report.threatsFound.size})"

        val text = buildString {
            appendLine("🛡️ ЗВІТ КІБЕР-АУДИТУ ЗСУ")
            appendLine("Пристрій: ${report.deviceModel} (${report.androidVersion})")
            appendLine("Час перевірки: ${report.scanTimestamp}")
            appendLine("Всього додатків: ${report.totalAppsScanned}")
            appendLine("Встановлено не з Play Store: ${report.sideloadedAppsCount}")
            appendLine("Статус системи: $statusText")
            if (!report.isSafe) {
                appendLine("Загрози:")
                report.threatsFound.forEach { threat ->
                    appendLine(" - ${threat.appName} (${threat.packageName}): ${threat.reasons.joinToString("; ")}")
                }
            }
            appendLine("Telegram-сесії: ПЕРЕВІРЕНО БІЙЦЕМ")
            appendLine("GPS-теги камери: ВИМКНЕНО")
        }

        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = ClipData.newPlainText("MilitaryAuditReport", text)
        clipboard.setPrimaryClip(clip)

        Toast.makeText(this, getString(R.string.report_copied), Toast.LENGTH_SHORT).show()
    }
}
