"""Pruebas de la interfaz con el mouse. Requiere la demo abierta (tests/reopen.sh) y la ventana del FX al frente.
REAPER a veces no le pasa a la grafica un clic inyectado (ver README): si una accion no cambio nada, se repite una
vez y se cuenta como "clic perdido"; la prueba falla si el valor sigue mal despues del reintento."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ui import *
fails = 0; lost = 0
def check(name, got, want):
    global fails
    ok = (want(got) if callable(want) else got == want); fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:46s} {got!r}")
def act(fn, n):
    """hace la accion y devuelve el valor del slider n; si no cambio, la repite una vez"""
    global lost
    v0 = param(n); fn(); v = param(n)
    if v == v0: lost += 1; print(f"    (clic perdido, se repite)"); fn(); v = param(n)
    return v

subprocess.run(["osascript", "-e", 'tell application "REAPER" to activate']); time.sleep(0.6)
cc(f"c:{pt(500, 5)}")
check("arranca con 'Pies en la arena' (empuje 6)", num(param(3)), 6.0)
check("modo armonicos del sub", param(1), "Armonicos del sub")
check("clic en Saturar todo", act(lambda: click(*MODE(1)), 1), "Saturar todo")
check("clic en Radio vieja", act(lambda: click(*MODE(2)), 1), "Radio vieja")
x, y = KNOB(0, 14); act(lambda: drag(x, y, x, y + 40), 11)
check("radio: arrastrar Cantidad hacia abajo baja", num(param(11)), lambda v: v < 100)
dclick(x, y); check("radio: doble clic en Cantidad = 100", num(param(11)), 100.0)
x, y = KNOB(3, 14); cc(f"m:{pt(x, y)}"); f0 = num(param(12))
check("radio: rueda sobre Graves cambia", num(act(lambda: wheel(5), 12)), lambda v: v != f0)
check("clic en Armonicos del sub", act(lambda: click(*MODE(0)), 1), "Armonicos del sub")
check("tipo Cinta", act(lambda: click(*TYPE(1)), 2), "Cinta")
check("tipo Duro", act(lambda: click(*TYPE(3)), 2), "Duro")
check("tipo Suave", act(lambda: click(*TYPE(0)), 2), lambda v: v.startswith("Suave"))
g0 = num(param(3)); x, y = KNOB(0)
check("arrastrar Empuje hacia arriba sube", num(act(lambda: drag(x, y, x, y - 40), 3)), lambda v: v > g0 + 1)
check("doble clic en Empuje = 6", num(act(lambda: dclick(x, y), 3)), 6.0)
check("arrastrar en la grafica sube el empuje", num(act(lambda: drag(*GRAPH, GRAPH[0], GRAPH[1] - 60), 3)), lambda v: 8 < v < 12)
x, y = KNOB(2); cc(f"m:{pt(x, y)}"); f0 = num(param(5))
check("rueda sobre Corte cambia", num(act(lambda: wheel(5), 5)), lambda v: v != f0)
check("pendiente 24 dB/oct", act(lambda: click(*SLOPE), 7), lambda v: v.startswith("24"))
check("pendiente 12 dB/oct", act(lambda: click(*SLOPE), 7), lambda v: v.startswith("12"))
check("oversampling 8x", act(lambda: click(*OS), 22), "8x")
check("oversampling apagado", act(lambda: click(*OS), 22), "Apagado")
check("oversampling 4x", act(lambda: click(*OS), 22), "4x")
check("escuchar cambios", act(lambda: click(*DELTA), 23), lambda v: v.startswith("Solo"))
check("escuchar cambios apagado", act(lambda: click(*DELTA), 23), "Normal")
def menu(): click(*PRESETS); time.sleep(0.6); cc("kp:arrow-down", "kp:return")
act(menu, 1)
check("menu Presets -> Nube baja radio X2", (param(1), num(param(12))), ("Radio vieja", 450.0))
print(f"FALLAS: {fails}   (clics perdidos y repetidos: {lost})")
sys.exit(1 if fails else 0)
