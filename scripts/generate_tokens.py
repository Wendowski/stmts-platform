"""Regenerate semantic colors from the unmodified designer token file."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
tokens=json.loads((root/'design/reference/tokens/design-tokens.json').read_text())
css=':root{'+''.join(f'--{k}:{v};' for k,v in tokens['color']['light'].items())+'}\n.dark{'+''.join(f'--{k}:{v};' for k,v in tokens['color']['dark'].items())+'}\n'
(root/'design/generated/tokens.css').write_text(css)
(root/'web/src/tokens.css').write_text(css)
swift='// Generated semantic colors. Native integration is pending.\nimport SwiftUI\nenum STMTSColors {\n'
kotlin='// Generated semantic colors. Native integration is pending.\npackage example.stmts\nimport androidx.compose.ui.graphics.Color\nobject STMTSColors {\n'
for theme,colors in tokens['color'].items():
 for name,value in colors.items():
  key=theme+''.join(s.title() for s in name.split('-'))
  number=int(value[1:],16)
  swift+=f'    static let {key} = Color(red: {((number>>16)&255)/255:.6f}, green: {((number>>8)&255)/255:.6f}, blue: {(number&255)/255:.6f})\n'
  kotlin+=f'    val {key} = Color(0xFF{value[1:]})\n'
swift+='}\n';kotlin+='}\n'
(root/'design/generated/STMTSColors.swift').write_text(swift)
(root/'design/generated/STMTSColors.kt').write_text(kotlin)
