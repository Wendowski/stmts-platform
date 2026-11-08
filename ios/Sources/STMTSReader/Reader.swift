import SwiftUI

struct Block: Decodable, Identifiable {
    let id: String
    let type: String
    let text: String
    let children: [Block]
    let depth: Int?
    var plain: String { text + children.map(\.plain).joined() }
}
struct Post: Decodable {
    struct Author: Decodable { let displayName: String; let handle: String }
    struct Content: Decodable { let blocks: [Block]; let excerpt: String; let readingMinutes: Int }
    let title: String; let summary: String; let author: Author; let content: Content
}
public struct STMTSPreview: View {
    @State private var post: Post?
    @State private var failed = false
    public init() {}
    public var body: some View {
        NavigationStack {
            Group {
                if let post {
                    List {
                        Section("Development preview · read only") {
                            NavigationLink {
                                ScrollView {
                                    VStack(alignment: .leading, spacing: 24) {
                                        Text(post.title).font(.largeTitle).fontDesign(.serif).accessibilityAddTraits(.isHeader)
                                        Text(post.summary).font(.title3).foregroundStyle(.secondary)
                                        Text(post.author.displayName).font(.headline)
                                        ForEach(post.content.blocks) { block in
                                            // Initial native text projection. Rich inline/table parity remains gated.
                                            if block.type == "heading" {
                                                Text(block.plain).font(.title2).fontDesign(.serif).accessibilityAddTraits(.isHeader)
                                            } else if block.type == "code" {
                                                ScrollView(.horizontal) { Text(block.text).font(.body.monospaced()).textSelection(.enabled) }.accessibilityLabel("Code")
                                            } else {
                                                Text(block.plain).font(.body).fontDesign(.serif).textSelection(.enabled)
                                            }
                                        }
                                    }.padding().frame(maxWidth: 680, alignment: .leading)
                                }.navigationTitle("Statement").navigationBarTitleDisplayMode(.inline)
                            } label: {
                                VStack(alignment: .leading, spacing: 12) {
                                    Text(post.author.displayName).font(.headline)
                                    Text(post.title).font(.title).fontDesign(.serif)
                                    Text(post.content.excerpt)
                                    Text("Continue reading · \(post.content.readingMinutes) min read").font(.caption)
                                }.padding(.vertical)
                            }
                        }
                    }
                } else if failed { ContentUnavailableView("Statement unavailable", systemImage: "doc.text") }
                else { ProgressView("Loading statement") }
            }.navigationTitle("STMTS").task {
                #if DEBUG
                do {
                    guard let url = Bundle.module.url(forResource: "post", withExtension: "json") else { failed = true; return }
                    post = try JSONDecoder().decode(Post.self, from: Data(contentsOf: url))
                } catch { failed = true }
                #else
                failed = true
                #endif
            }
        }
    }
}
