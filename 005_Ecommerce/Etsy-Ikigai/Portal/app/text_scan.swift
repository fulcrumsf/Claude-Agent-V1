// Ikigai text scan (realism addendum 6.2, 2026-11-20): macOS Vision OCR on a list of PNG tiles.
// Accurate recognition, no language correction, minimumTextHeight 0, so small garbled book-spine text is found.
// Usage: ikigai_text_scan tile1.png tile2.png ...   -> JSON on stdout:
//   [{"tile": 0, "conf": 0.8, "box": [x0, y0, x1, y1], "text": "..."}]   box in 0..1 of the tile, TOP-left origin.
// Compiled by app/scene_scan.py with `swiftc -O` into ~/.cache/ikigai-sam/bin/ikigai_text_scan (setting text_scan_bin).
import Foundation
import Vision
import AppKit

struct Hit: Codable { let tile: Int; let conf: Float; let box: [Double]; let text: String }

var hits: [Hit] = []
for (i, path) in CommandLine.arguments.dropFirst().enumerated() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    req.minimumTextHeight = 0
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    do { try handler.perform([req]) } catch { continue }
    for obs in req.results ?? [] {
        guard let top = obs.topCandidates(1).first else { continue }
        let b = obs.boundingBox
        hits.append(Hit(tile: i, conf: top.confidence,
                        box: [Double(b.minX), Double(1 - b.maxY), Double(b.maxX), Double(1 - b.minY)],
                        text: top.string))
    }
}
let enc = JSONEncoder()
if let d = try? enc.encode(hits), let s = String(data: d, encoding: .utf8) { print(s) } else { print("[]") }
