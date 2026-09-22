package ua.mil.cyberguard

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.button.MaterialButton
import ua.mil.cyberguard.utils.DeepLinkHelper

class ThreatAdapter(
    private val threats: List<SuspiciousApp>
) : RecyclerView.Adapter<ThreatAdapter.ThreatViewHolder>() {

    class ThreatViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val ivIcon: ImageView = itemView.findViewById(R.id.iv_app_icon)
        val tvAppName: TextView = itemView.findViewById(R.id.tv_app_name)
        val tvPackageName: TextView = itemView.findViewById(R.id.tv_package_name)
        val tvReasons: TextView = itemView.findViewById(R.id.tv_threat_reasons)
        val btnManagePerms: MaterialButton = itemView.findViewById(R.id.btn_manage_perms)
        val btnDisableAccessibility: MaterialButton = itemView.findViewById(R.id.btn_disable_accessibility)
        val btnUninstall: MaterialButton = itemView.findViewById(R.id.btn_uninstall)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ThreatViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_threat, parent, false)
        return ThreatViewHolder(view)
    }

    override fun onBindViewHolder(holder: ThreatViewHolder, position: Int) {
        val item = threats[position]
        holder.tvAppName.text = item.appName
        holder.tvPackageName.text = item.packageName
        if (item.icon != null) {
            holder.ivIcon.setImageDrawable(item.icon)
        } else {
            holder.ivIcon.setImageResource(R.mipmap.ic_launcher)
        }

        holder.tvReasons.text = item.reasons.joinToString("\n")

        // 1. Керування дозволами через App Settings (мікрофон, камера, геолокація, сповіщення)
        holder.btnManagePerms.setOnClickListener {
            DeepLinkHelper.openAppSettings(it.context, item.packageName)
        }

        // 2. Спецдоступ (Служба доступності) - показуємо тільки якщо додаток зареєстрував AccessibilityService
        if (item.hasAccessibility) {
            holder.btnDisableAccessibility.visibility = View.VISIBLE
            holder.btnDisableAccessibility.setOnClickListener {
                DeepLinkHelper.openAccessibilitySettings(it.context)
            }
        } else {
            holder.btnDisableAccessibility.visibility = View.GONE
        }

        // 3. Видалення додатка
        holder.btnUninstall.setOnClickListener {
            DeepLinkHelper.uninstallPackage(it.context, item.packageName)
        }
    }

    override fun getItemCount(): Int = threats.size
}
