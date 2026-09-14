import Foundation
import Vision
import ImageIO
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let request = VNDetectFaceLandmarksRequest()
do {
 let handler = VNImageRequestHandler(url: url, options: [:])
 try handler.perform([request])
 let faces = (request.results ?? []).sorted { $0.boundingBox.width * $0.boundingBox.height > $1.boundingBox.width * $1.boundingBox.height }
 var output: [String: Any] = ["faces": faces.count]
 if let face = faces.first {
  let b = face.boundingBox
  output["bbox"] = [b.minX, 1-b.maxY, b.width, b.height]
  func points(_ r: VNFaceLandmarkRegion2D?) -> [[Double]] {
   guard let r = r else {return []}
   return r.normalizedPoints.map { p in [Double(b.minX + CGFloat(p.x)*b.width), Double(1-b.minY-CGFloat(p.y)*b.height)] }
  }
  output["left_eye"] = points(face.landmarks?.leftEye)
  output["right_eye"] = points(face.landmarks?.rightEye)
  output["mouth"] = points(face.landmarks?.outerLips)
 }
 let data = try JSONSerialization.data(withJSONObject: output, options: [.sortedKeys])
 print(String(data:data,encoding:.utf8)!)
} catch { print("{\"faces\":0,\"error\":\"Vision could not analyze this image\"}") }
