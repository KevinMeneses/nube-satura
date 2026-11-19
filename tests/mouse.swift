// Arrastre con el mouse: swift tests/mouse.swift x0 y0 x1 y1 [pasos]
// Apretón con clickState = 1 y eventos leftMouseDragged (cliclick a veces pierde el apretón después de un doble clic).
import CoreGraphics
import Foundation
let a = CommandLine.arguments.dropFirst().compactMap { Double($0) }
let (x0, y0, x1, y1) = (a[0], a[1], a[2], a[3]); let steps = a.count > 4 ? Int(a[4]) : 8
func post(_ t: CGEventType, _ x: Double, _ y: Double) {
    let e = CGEvent(mouseEventSource: nil, mouseType: t, mouseCursorPosition: CGPoint(x: x, y: y), mouseButton: .left)!
    e.setIntegerValueField(.mouseEventClickState, value: 1); e.post(tap: .cghidEventTap)
}
post(.mouseMoved, x0, y0); usleep(150000)
post(.leftMouseDown, x0, y0); usleep(150000)
for k in 1...steps {
    let f = Double(k) / Double(steps); post(.leftMouseDragged, x0 + (x1 - x0) * f, y0 + (y1 - y0) * f); usleep(60000)
}
usleep(100000); post(.leftMouseUp, x1, y1); usleep(150000)
