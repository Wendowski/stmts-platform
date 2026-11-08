package example.stmts
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import org.json.JSONObject

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { ReaderPreview() } }
    }
}
private fun plain(node: JSONObject): String {
    val children = node.getJSONArray("children")
    return node.getString("text") + (0 until children.length()).joinToString("") { plain(children.getJSONObject(it)) }
}
@Composable fun ReaderPreview() {
    val context = LocalContext.current
    var reading by remember { mutableStateOf(false) }
    val post = remember { if (!BuildConfig.DEBUG) null else runCatching { JSONObject(context.assets.open("post.json").bufferedReader().use { it.readText() }) }.getOrNull() }
    Surface(Modifier.fillMaxSize()) {
        if (post == null) { Text("Statement unavailable", Modifier.padding(24.dp)) }
        else LazyColumn(contentPadding = PaddingValues(24.dp), verticalArrangement = Arrangement.spacedBy(20.dp)) {
            item { Text("STMTS · Development preview · read only", style = MaterialTheme.typography.labelLarge) }
            item { Text(post.getString("title"), style = MaterialTheme.typography.headlineLarge, fontFamily = FontFamily.Serif) }
            item { Text(post.getJSONObject("author").getString("displayName")) }
            if (!reading) {
                item { Text(post.getJSONObject("content").getString("excerpt")) }
                item { Button(onClick = { reading = true }, modifier = Modifier.heightIn(min = 48.dp)) { Text("Continue reading") } }
            } else {
                item { Button(onClick = { reading = false }) { Text("Back to Discover") } }
                val blocks = post.getJSONObject("content").getJSONArray("blocks")
                items(blocks.length(), key = { blocks.getJSONObject(it).getString("id") }) { index ->
                    val block = blocks.getJSONObject(index)
                    // Initial text projection; rich inline/table parity is still pending.
                    Text(plain(block), style = if (block.getString("type") == "heading") MaterialTheme.typography.headlineSmall else MaterialTheme.typography.bodyLarge, fontFamily = if (block.getString("type") == "code") FontFamily.Monospace else FontFamily.Serif)
                }
            }
        }
    }
}
