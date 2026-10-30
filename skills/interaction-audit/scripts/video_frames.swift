// Turns a screen recording into one PNG strip of evenly spaced frames, so an
// animation can be judged (and shown in a report or chat) as a still image.
// macOS only, no ffmpeg needed:
//   swift video_frames.swift <video> <out.png> <from-s> <to-s> <count> [full|top|bottom] [frame-width]
import AVFoundation
import AppKit

let args = CommandLine.arguments
guard args.count >= 6, let from = Double(args[3]), let to = Double(args[4]), let count = Int(args[5]), count > 0 else {
    FileHandle.standardError.write("usage: video_frames <video> <out.png> <from-s> <to-s> <count> [full|top|bottom] [frame-width]\n".data(using: .utf8)!)
    exit(2)
}
let crop = args.count > 6 ? args[6] : "full"
let frameWidth = args.count > 7 ? Int(args[7]) ?? 240 : 240

let generator = AVAssetImageGenerator(asset: AVURLAsset(url: URL(fileURLWithPath: args[1])))
generator.requestedTimeToleranceBefore = .zero
generator.requestedTimeToleranceAfter = .zero
generator.maximumSize = CGSize(width: frameWidth, height: frameWidth * 4)

var frames: [CGImage] = []
for i in 0..<count {
    let t = from + (to - from) * Double(i) / Double(max(count - 1, 1))
    guard let image = try? generator.copyCGImage(at: CMTime(seconds: t, preferredTimescale: 600), actualTime: nil) else { continue }
    let half = image.height / 2
    // CGImage rows start at the top, so "top" is y 0.
    let rect: CGRect
    switch crop {
    case "top": rect = CGRect(x: 0, y: 0, width: image.width, height: half)
    case "bottom": rect = CGRect(x: 0, y: half, width: image.width, height: image.height - half)
    default: rect = CGRect(x: 0, y: 0, width: image.width, height: image.height)
    }
    if let part = image.cropping(to: rect) { frames.append(part) }
}
guard let first = frames.first else {
    FileHandle.standardError.write("no frames read from \(args[1])\n".data(using: .utf8)!)
    exit(1)
}

let gap = 4
let width = frames.count * first.width + (frames.count - 1) * gap
let context = CGContext(data: nil, width: width, height: first.height, bitsPerComponent: 8, bytesPerRow: 0,
                        space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
context.setFillColor(gray: 0.5, alpha: 1)
context.fill(CGRect(x: 0, y: 0, width: width, height: first.height))
for (i, frame) in frames.enumerated() {
    context.draw(frame, in: CGRect(x: i * (first.width + gap), y: 0, width: first.width, height: first.height))
}
let png = NSBitmapImageRep(cgImage: context.makeImage()!).representation(using: .png, properties: [:])!
try png.write(to: URL(fileURLWithPath: args[2]))
print("\(frames.count) frames → \(args[2])")
