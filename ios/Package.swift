// swift-tools-version: 6.0
import PackageDescription
let package = Package(name: "STMTSReader", platforms: [.iOS(.v17)], products: [.library(name: "STMTSReader", targets: ["STMTSReader"])], targets: [.target(name: "STMTSReader", resources: [.process("Resources")])])
