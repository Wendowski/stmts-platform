# Native adaptation
Examples are integration snippets, not complete compiled native projects. design-tokens.json is the source for generation. Swift example uses UIKit through SwiftUI; add explicit `import UIKit` if needed by the target. Set minimum OS versions and dependencies in the implementation repository.

| Intent | iOS / iPadOS | Android |
|---|---|---|
| Navigation | TabView compact; NavigationSplitView regular; standard back | Compose Navigation; adaptive rail/bar; system back |
| Sheet | Platform presentation detents/full-screen editor | ModalBottomSheet/full-screen editor |
| Reading | Native text blocks with accessibility headings | Native text composables with heading semantics |
| Media selection | PhotosPicker, permission-minimal | System Photo Picker, permission-minimal |
| Share | ShareLink / system share sheet | ACTION_SEND system chooser |
| Editing | Native text editor with source selection adapter | Native text input with selection-aware toolbar |
| Type | System serif with Dynamic Type | Serif with sp and fontScale |
| Haptics | Optional on deliberate action; obey settings | Optional system haptics; obey settings |

Do not port CSS pixel layouts into fixed native constraints. iPad multitasking, landscape, hardware keyboards, Android foldables, TalkBack/VoiceOver, display scaling and safe-area/IME insets need actual device verification. Native source editors must preserve selection/composition when applying formatting; test CJK IME and emoji. Avoid all-body attributed text if it prevents accessible headings or reliable inline media. Use a canonical block-to-native-view renderer and a shared fixture corpus.
