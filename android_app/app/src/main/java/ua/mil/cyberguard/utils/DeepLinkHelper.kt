package ua.mil.cyberguard.utils

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.Settings
import android.widget.Toast

object DeepLinkHelper {

    fun openTelegramDevices(context: Context) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse("tg://settings/devices"))
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(intent)
        } catch (e: Exception) {
            try {
                // Якщо прямий deep-link не підтримується конкретним клієнтом — відкриваємо додаток Telegram
                val launchIntent = context.packageManager.getLaunchIntentForPackage("org.telegram.messenger")
                if (launchIntent != null) {
                    context.startActivity(launchIntent)
                    Toast.makeText(context, "Перейдіть: Налаштування -> Пристрої", Toast.LENGTH_LONG).show()
                } else {
                    Toast.makeText(context, "Telegram не встановлено на цьому пристрої", Toast.LENGTH_SHORT).show()
                }
            } catch (ex: Exception) {
                Toast.makeText(context, "Не вдалося відкрити Telegram", Toast.LENGTH_SHORT).show()
            }
        }
    }

    fun openApplicationSettings(context: Context) {
        try {
            val intent = Intent(Settings.ACTION_APPLICATION_SETTINGS)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(context, "Відкрийте налаштування камери вручну", Toast.LENGTH_SHORT).show()
        }
    }

    fun uninstallPackage(context: Context, packageName: String) {
        try {
            val intent = Intent(Intent.ACTION_DELETE).apply {
                data = Uri.parse("package:$packageName")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(context, "Не вдалося ініціювати видалення", Toast.LENGTH_SHORT).show()
        }
    }
}
