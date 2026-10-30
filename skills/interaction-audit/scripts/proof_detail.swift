// Cuts the problem area out of a screenshot, scales it up and frames the spot,
// so a finding's proof is readable at a glance in the report or chat.
// macOS only, no extra installs:
//   swift proof_detail.swift <in.png> <out.png> <x> <y> <w> <h> [margin] [min-width]
// x, y, w, h are in the screenshot's pixels and mark the problem; margin
// (default 40) adds context around it; the result is scaled up to at least
// min-width pixels (default 900) and the marked area gets a red frame.
import AppKit

let args = CommandLine.arguments
guard args.count >= 7, let x = Double(args[3]), let y = Double(args[4]),
      let w = Double(args[5]), let h = Double(args[6]) else {
    FileHandle.standardError.write("usage: proof_detail <in.png> <out.png> <x> <y> <w> <h> [margin] [min-width]\n".data(using: .utf8)!)
    exit(2)
}
let margin = args.count > 7 ? Double(args[7]) ?? 40 : 40
let minWidth = args.count > 8 ? Double(args[8]) ?? 900 : 900

guard let src = NSImage(contentsOfFile: args[1]),
      let cg = src.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    FileHandle.standardError.write("cannot read \(args[1])\n".data(using: .utf8)!)
    exit(1)
}
let imgW = Double(cg.width), imgH = Double(cg.height)
let cx = max(0, x - margin), cy = max(0, y - margin)
let cw = min(imgW - cx, w + 2 * margin), ch = min(imgH - cy, h + 2 * margin)
guard cw > 0, ch > 0, let crop = cg.cropping(to: CGRect(x: cx, y: cy, width: cw, height: ch)) else {
    FileHandle.standardError.write("area outside the image (\(Int(imgW))×\(Int(imgH)))\n".data(using: .utf8)!)
    exit(1)
}
let scale = max(1, minWidth / cw)
let outW = Int(cw * scale), outH = Int(ch * scale)
guard let ctx = CGContext(data: nil, width: outW, height: outH, bitsPerComponent: 8, bytesPerRow: 0,
                          space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { exit(1) }
// Nearest neighbour keeps pixel text crisp when scaling up.
ctx.interpolationQuality = scale > 1 ? .none : .high
ctx.draw(crop, in: CGRect(x: 0, y: 0, width: outW, height: outH))
// CoreGraphics has its origin bottom left; the marked rect is given top left.
let fx = (x - cx) * scale, fy = Double(outH) - (y - cy + h) * scale
ctx.setStrokeColor(CGColor(red: 0.86, green: 0.1, blue: 0.1, alpha: 1))
ctx.setLineWidth(max(3, 2 * scale))
ctx.stroke(CGRect(x: fx, y: fy, width: w * scale, height: h * scale).insetBy(dx: -4, dy: -4))
guard let out = ctx.makeImage(),
      let png = NSBitmapImageRep(cgImage: out).representation(using: .png, properties: [:]) else { exit(1) }
try png.write(to: URL(fileURLWithPath: args[2]))
print("\(args[2]) \(outW)×\(outH)")
