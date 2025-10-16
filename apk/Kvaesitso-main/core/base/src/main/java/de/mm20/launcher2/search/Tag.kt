package de.mm20.launcher2.search

import android.content.Context
import android.os.Bundle
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Tag
import de.mm20.launcher2.icons.ColorLayer
import de.mm20.launcher2.icons.StaticLauncherIcon
import de.mm20.launcher2.icons.VectorLayer

data class Tag(
    val tag: String,
    override val labelOverride: String? = null
): SavableSearchable {

    override val domain: String = Domain

    override val key: String = "$domain://$tag"
    override val label: String = tag

    override val preferDetailsOverLaunch: Boolean = true

    override fun launch(context: Context, options: Bundle?): Boolean {
        return false
    }
    override fun overrideLabel(label: String): SavableSearchable {
        return this.copy(labelOverride = label)
    }

    override fun getPlaceholderIcon(context: Context): StaticLauncherIcon {
        return StaticLauncherIcon(
            foregroundLayer = VectorLayer(Icons.Rounded.Tag),
            backgroundLayer = ColorLayer()
        )
    }

    override fun getSerializer(): SearchableSerializer {
        return TagSerializer()
    }

    companion object {
        const val Domain = "tag"
    }
}