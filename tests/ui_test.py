"""Pruebas de la interfaz con el mouse. Requiere la demo abierta (tests/reopen.sh) y la ventana del FX al frente."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ui import *
fails = 0
def check(name, got, want):
    global fails
    ok = (want(got) if callable(want) else got == want); fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:46s} {got!r}")

subprocess.run(["osascript", "-e", 'tell application "REAPER" to activate']); time.sleep(0.6)
cc(f"c:{pt(500, 5)}")
check("arranca con 'Pies en la arena' (empuje 6)", num(param(3)), 6.0)
check("modo armonicos del sub", param(1), "Armonicos del sub")
click(*MODE(1)); check("clic en Saturar todo", param(1), "Saturar todo")
click(*MODE(2)); check("clic en Radio vieja", param(1), "Radio vieja")
x, y = KNOB(0, 14); dclick(x, y); check("radio: doble clic en Cantidad = 100", num(param(11)), 100.0)
x, y = KNOB(3, 14); cc(f"m:{pt(x, y)}"); f0 = num(param(12)); wheel(5)
check("radio: rueda sobre Graves cambia", num(param(12)), lambda v: v != f0)
click(*MODE(0)); check("clic en Armonicos del sub", param(1), "Armonicos del sub")
click(*TYPE(1)); check("tipo Cinta", param(2), "Cinta")
click(*TYPE(3)); check("tipo Duro", param(2), "Duro")
click(*TYPE(0)); check("tipo Suave", param(2), lambda v: v.startswith("Suave"))
g0 = num(param(3)); x, y = KNOB(0); drag(x, y, x, y - 40)
check("arrastrar Empuje hacia arriba sube", num(param(3)), lambda v: v > g0 + 1)
dclick(x, y); check("doble clic en Empuje = 6", num(param(3)), 6.0)
drag(*GRAPH, GRAPH[0], GRAPH[1] - 60)
check("arrastrar en la grafica sube el empuje", num(param(3)), lambda v: 8 < v < 12)
x, y = KNOB(2); cc(f"m:{pt(x, y)}"); f0 = num(param(5)); wheel(5)
check("rueda sobre Corte cambia", num(param(5)), lambda v: v != f0)
click(*SLOPE); check("pendiente 24 dB/oct", param(7), lambda v: v.startswith("24"))
click(*SLOPE); check("pendiente 12 dB/oct", param(7), lambda v: v.startswith("12"))
click(*OS); check("oversampling 8x", param(22), "8x")
click(*OS); check("oversampling apagado", param(22), "Apagado")
click(*OS); check("oversampling 4x", param(22), "4x")
click(*DELTA); check("escuchar cambios", param(23), lambda v: v.startswith("Solo"))
click(*DELTA); check("escuchar cambios apagado", param(23), "Normal")
click(*PRESETS); time.sleep(0.6); cc("kp:arrow-down", "kp:return")
check("menu Presets -> Nube baja radio X2", (param(1), num(param(12))), ("Radio vieja", 450.0))
print("FALLAS:", fails)
sys.exit(1 if fails else 0)
