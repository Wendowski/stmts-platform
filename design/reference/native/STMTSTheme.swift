// SwiftUI token integration example; verify in the target Xcode project.
import SwiftUI

enum STMTSTheme {
    static func color(_ light: UInt32, _ dark: UInt32) -> Color {
        Color(uiColor: UIColor { trait in
            let hex = trait.userInterfaceStyle == .dark ? dark : light
            return UIColor(red: CGFloat((hex >> 16) & 255) / 255,
                           green: CGFloat((hex >> 8) & 255) / 255,
                           blue: CGFloat(hex & 255) / 255, alpha: 1)
        })
    }
    static let canvas = color(0xF7F7F2, 0x151B18)
    static let surface = color(0xFFFFFF, 0x1D2520)
    static let ink = color(0x202A24, 0xEDF1E9)
    static let muted = color(0x626D65, 0xB1BDB2)
    static let accent = color(0x285C43, 0xA8D5B6)
    static let onAccent = color(0xFFFFFF, 0x15271C)
    static let line = color(0xD9DFD7, 0x46554A)
    static let accentSoft = color(0xE8EFE4, 0x283E30)
    static let danger = color(0xA32E33, 0xFFB4B4)
    static let focus = color(0x245BC4, 0xAFC7FF)
    static let controlRadius: CGFloat = 10
    static let mediaRadius: CGFloat = 12
    static let minTarget: CGFloat = 44
}
struct STMTSReadingText: View {
    let text: String
    @ScaledMetric(relativeTo: .body) private var readingSize = 20
    var body: some View {
        Text(text).font(.system(size: readingSize, design: .serif))
            .foregroundStyle(STMTSTheme.ink).lineSpacing(6)
            .textSelection(.enabled).fixedSize(horizontal: false, vertical: true)
    }
}
// Apply appearance override via preferredColorScheme at root for Light/Dark;
// nil means System. Use NavigationSplitView on regular-width iPad and
// NavigationStack + TabView in compact widths. Honor safe areas and Dynamic Type.
