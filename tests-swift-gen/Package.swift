// swift-tools-version:5.5
import PackageDescription

let package = Package(
    name: "SwiftSerializationTest",
    platforms: [
        .macOS(.v12)
    ],
    dependencies: [
        .package(url: "https://github.com/MaxDesiatov/XMLCoder.git", from: "0.13.1"),
        .package(url: "https://github.com/jpsim/Yams.git", from: "5.0.0")
    ],
    targets: [
        .executableTarget(
            name: "SwiftSerializationTest",
            dependencies: [
                .product(name: "XMLCoder", package: "XMLCoder"),
                .product(name: "Yams", package: "Yams")
            ]
        )
    ]
)
