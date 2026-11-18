// Id de la ventana de REAPER cuyo titulo contiene el texto dado (para capturarla con screencapture -l aunque este
// tapada, sin mover el mouse ni robar el foco): swift tests/winshot.swift "Nube Satura"
import CoreGraphics
let want = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "Nube Satura"
let l = CGWindowListCopyWindowInfo([.optionAll], kCGNullWindowID) as! [[String: Any]]
for w in l {
    let n = (w[kCGWindowName as String] as? String) ?? ""; let o = (w[kCGWindowOwnerName as String] as? String) ?? ""
    if o == "REAPER" && n.contains(want) { print(w[kCGWindowNumber as String]!, n) }
}
