package de.mm20.launcher2.widgets

import android.app.Activity
import android.appwidget.AppWidgetHost
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import de.mm20.launcher2.database.entities.PartialWidgetEntity
import de.mm20.launcher2.ktx.tryStartActivity
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.util.UUID


@Serializable
data class WeatherWidgetConfig(
    val showForecast: Boolean = true,
)

data class WeatherWidget(
    override val id: UUID,
    val config: WeatherWidgetConfig = WeatherWidgetConfig(),
) : Widget() {

    override fun toDatabaseEntity(): PartialWidgetEntity {
        return PartialWidgetEntity(
            id = id,
            type = Type,
            config = Json.encodeToString(config),
        )
    }

    companion object {
        const val Type = "weather"
    }
}