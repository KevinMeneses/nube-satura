"""Ayudante para probar la interfaz con cliclick (ventana del FX en su posición/tamaño por defecto)."""
import subprocess, time, pathlib, re
WX, WY = 32, 65 + 53            # esquina del área gráfica del FX (puntos), bajo la cabecera de REAPER
ROOT = pathlib.Path(__file__).resolve().parent.parent
def pt(x, y): return f"{round(WX + x)},{round(WY + y)}"
def front():
    """trae REAPER al frente: si otra app tiene el foco, macOS usa el primer clic solo para activar la ventana"""
    subprocess.run(["osascript", "-e", 'tell application "REAPER" to activate'], check=True)
def cc(*args):
    if args[0][:2] in ("c:", "dc", "dd"): front()
    subprocess.run(["cliclick", "-w", "150", *args], check=True); time.sleep(0.4)
def wheel(n): subprocess.run(["swift", str(ROOT / "tests/scroll.swift"), str(n)], check=True); time.sleep(0.4)
def shot(path): subprocess.run(["screencapture", "-x", "-R32,65,1000,693", path], check=True); return path
def dump():
    p = ROOT / "tests/out/dump.txt"; p.unlink(missing_ok=True)
    # el REAPER -nonewinst es otro proceso "REAPER" que macOS activa un momento: hay que esperar a que termine y
    # devolver el foco a la instancia de la prueba, o el siguiente clic solo activa la ventana y no le llega al FX
    pr = subprocess.Popen(["/Applications/REAPER.app/Contents/MacOS/REAPER", "-nonewinst", str(ROOT / "tests/ui_dump.lua")],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = "(sin respuesta)"
    for _ in range(40):
        if p.exists() and "done" in p.read_text(): out = p.read_text().replace("done\n", ""); break
        time.sleep(0.25)
    try: pr.wait(5)
    except subprocess.TimeoutExpired: pass
    front(); time.sleep(0.3)
    return out
def param(n):
    """valor formateado del slider n"""
    m = re.search(rf"^{n} (.*)$", dump(), re.M); return m.group(1).rsplit(" = ", 1)[1] if m else None
def num(s): return float(s.split()[0]) if s else float("nan")
def flush():
    """REAPER a veces no le pasa a la gráfica un "soltar" (medido: mouse_cap queda en 1 con el botón suelto) y el
    apretón siguiente no cuenta como clic. Un clic en el pie (zona sin controles) lo limpia; si no estaba pegado, no hace nada."""
    q = pt(500, 627); cc(f"m:{q}", f"dd:{q}", f"du:{q}"); time.sleep(0.3)
def click(x, y):
    """mover, apretar y soltar con 60 ms entre cada uno: un clic instantaneo puede caer entre dos cuadros (60 Hz)"""
    flush(); p = pt(x, y); cc(f"m:{p}", f"dd:{p}", f"du:{p}")
def dclick(x, y):
    """doble clic a velocidad humana: el dc: de cliclick es tan rápido que a veces la gráfica no ve el último soltar
    y el JSFX cree que el botón sigue apretado (el clic siguiente se pierde)"""
    flush(); p = pt(x, y); cc(f"m:{p}", f"dd:{p}", f"du:{p}", f"dd:{p}", f"du:{p}")
def drag(x0, y0, x1, y1, steps=8):
    """arrastre con CGEvent (tests/mouse.swift): cliclick a veces pierde el apretón después de un doble clic"""
    flush(); front(); subprocess.run(["swift", str(ROOT / "tests/mouse.swift"), *map(str, (WX + x0, WY + y0, WX + x1, WY + y1, steps))], check=True)
    time.sleep(0.4)
# layout (ventana 1000x640): dy = 54, dh = 400, py = 464; curva en x 756..986, medidores 648..744, grafica 40..634
PY = 464
MODE = lambda k: (58 + k * 140 + 68, PY + 20)
TYPE = lambda k: (528 + k * 74 + 35, PY + 20)
def KNOB(i, n=6):
    ks = min(88, (1000 - 28) / n); return (14 + ks / 2 + i * ks, PY + 92)
SLOPE = (671, PY + 121)
PRESETS, OS, DELTA = (208, 22), (344, 22), (490, 22)
GRAPH = (337, 254)
