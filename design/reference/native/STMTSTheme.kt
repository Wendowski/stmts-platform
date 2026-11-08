// Compose token integration example; integrate in the target Android project.
package com.stmts.design
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.TextStyle

data class STMTSColors(val canvas: Color, val surface: Color, val ink: Color,
    val muted: Color, val accent: Color, val onAccent: Color, val line: Color,
    val accentSoft: Color, val danger: Color, val focus: Color)
val STMTSLight = STMTSColors(Color(0xFFF7F7F2), Color(0xFFFFFFFF), Color(0xFF202A24),
    Color(0xFF626D65), Color(0xFF285C43), Color(0xFFFFFFFF), Color(0xFFD9DFD7),
    Color(0xFFE8EFE4), Color(0xFFA32E33), Color(0xFF245BC4))
val STMTSDark = STMTSColors(Color(0xFF151B18), Color(0xFF1D2520), Color(0xFFEDF1E9),
    Color(0xFFB1BDB2), Color(0xFFA8D5B6), Color(0xFF15271C), Color(0xFF46554A),
    Color(0xFF283E30), Color(0xFFFFB4B4), Color(0xFFAFC7FF))
val STMTSReading = TextStyle(fontFamily = FontFamily.Serif, fontSize = 20.sp, lineHeight = 34.sp)
val STMTSMinTarget = 48.dp
val STMTSControlRadius = 10.dp
// Provide chosen colors through CompositionLocal at app root. Map semantic
// colors into MaterialTheme rather than accepting default dynamic color.
// Keep sp scaling enabled, use sizeIn(minWidth=48.dp,minHeight=48.dp) on actions,
// and switch navigation based on available window size rather than model name.
