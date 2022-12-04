package banned.mirai

import net.mamoe.mirai.console.plugin.jvm.JvmPluginDescription
import net.mamoe.mirai.console.plugin.jvm.KotlinPlugin
import net.mamoe.mirai.utils.info

object RssParser : KotlinPlugin(
        JvmPluginDescription(
                id = "banned.mirai.rss-parser",
                name = "Rss Parser",
                version = "0.1.0",
                            ) {
            author("banned")
        }
                               )
{
    override fun onEnable()
    {
        logger.info { "Plugin loaded" }
    }
}