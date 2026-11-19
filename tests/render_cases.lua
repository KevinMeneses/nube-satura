-- Carga Nube Satura (o los JSFX originales) en una pestaña nueva, renderiza cada caso y cierra la pestaña.
-- Uso: REAPER -nonewinst tests/render_cases.lua   (escribe tests/out/*.wav y tests/out/log.txt)
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
local FX = "JS:Nube Satura/nube_satura.jsfx"
local PRESET = 24
os.execute('mkdir -p "' .. OUT .. '"')
local logf = io.open(OUT .. "/log.txt", "w")
local function log(...) local t = {} for _, v in ipairs({...}) do t[#t+1] = tostring(v) end logf:write(table.concat(t, " "), "\n") logf:flush() end
local function with(a, b) local r = {} for k, v in pairs(a) do r[k] = v end for k, v in pairs(b or {}) do r[k] = v end return r end

-- JSFX originales (claude_sub_sat: kick largo de "Pies en la arena"; claude_radio: Outro 2 de "Nube baja")
local SUB, RAD = "JS:Claude/claude_sub_sat.jsfx", "JS:Claude/claude_radio.jsfx"
-- radio: Desde 0 y Rampa 0 (efecto completo desde el principio), estatica -80 (el ruido es aleatorio)
local RDEF = {0, 0, 450, 3200, 4, 6, -80, 12, 30, 0, 0, 1, -80, 3000}
local RX4 = {0, 0, 100, 8000, 1, 2, -80, 4, 75, 0.7, 0, 1, -80, 3000}
local RLOFI = {0, 0, 20, 20000, 0, 0, -80, 0, 100, 0, 9.5, 2.5, -10, 3000}
local RSTAT = {0, 0, 450, 3200, 4, 6, -40, 12, 30, 0, 0, 1, -80, 3000}
local RADIO = {[1] = 2, [4] = 0, [15] = -80}

-- {nombre, señal, parámetros de Nube Satura}  o  {nombre, señal, nil, cadena = {{fx, {valores}}, ...}}
local CASES = {
  -- igual que los originales (sin oversampling)
  {"eq_sub_ref", "music.wav", nil, chain = {{SUB, {150, 6, 0.4, 90, 0}}}},
  {"eq_sub", "music.wav", {[22] = 0}},
  {"eq_sub808_ref", "808.wav", nil, chain = {{SUB, {150, 6, 0.4, 90, 0}}}},
  {"eq_sub808", "808.wav", {[22] = 0}},
  {"eq_radio_ref", "music.wav", nil, chain = {{RAD, RDEF}}},
  {"eq_radio", "music.wav", with(RADIO, {[22] = 0})},
  {"eq_x4_ref", "music.wav", nil, chain = {{RAD, RX4}}},
  {"eq_x4", "music.wav", {[PRESET] = 2, [15] = -80, [22] = 0}},
  {"eq_lofi_ref", "music.wav", nil, chain = {{RAD, RLOFI}}},
  {"eq_lofi", "music.wav", {[PRESET] = 3, [15] = -80, [20] = -10, [22] = 0}},
  {"static_ref", "silence.wav", nil, chain = {{RAD, RSTAT}}},
  {"static", "silence.wav", {[1] = 2, [4] = 0, [15] = -40, [22] = 0}},
  -- con oversampling, contra los originales
  {"os_sub", "music.wav", {[PRESET] = 4}},
  {"os8_sub", "808.wav", {[22] = 2}},
  {"os_radio", "music.wav", RADIO},
  -- contra el modelo en numpy
  {"m_todo_off_valv", "music.wav", {[1] = 1, [2] = 2, [3] = 9, [22] = 0}},
  {"m_todo8", "music.wav", {[1] = 1, [2] = 3, [3] = 18, [22] = 2}},
  {"m_radio_os", "music.wav", {[1] = 2, [15] = -80, [4] = 0.3, [2] = 1}},
  {"m_lofi_os8", "music.wav", {[1] = 2, [15] = -80, [22] = 2, [18] = 8, [19] = 3.25, [20] = -20, [12] = 20, [13] = 20000}},
  {"m_amt50", "music.wav", {[1] = 2, [15] = -80, [11] = 50}},
  {"m_delta", "music.wav", {[23] = 1, [7] = 1, [3] = 12}},
  -- teoria
  {"fund_12", "s50_m6.wav", {[3] = 12, [4] = 0.3, [5] = 120, [6] = 100, [7] = 0}},
  {"fund_24", "s50_m6.wav", {[3] = 12, [4] = 0.3, [5] = 120, [6] = 100, [7] = 1}},
  {"phone808", "808.wav", {[PRESET] = 5}},
  {"latency_os", "burst.wav", {[1] = 1, [3] = 6}},
  {"latency_off", "burst.wav", {[1] = 1, [3] = 6, [22] = 0}},
  {"latency_radio", "burst.wav", {[1] = 2, [15] = -80, [16] = 0, [12] = 20, [13] = 20000, [14] = 0, [17] = 100}},
  {"null_amt0", "music.wav", {[1] = 2, [11] = 0}},
  {"null_mix0", "music.wav", {[1] = 1, [9] = 0, [2] = 3, [3] = 18}},
  {"alias_music_off", "music.wav", {[1] = 1, [2] = 3, [3] = 12, [4] = 0, [22] = 0}},
  {"alias_music_os", "music.wav", {[1] = 1, [2] = 3, [3] = 12, [4] = 0, [22] = 1}},
}
for t = 0, 3 do
  CASES[#CASES + 1] = {"m_sub_t" .. t, "808.wav", {[2] = t, [7] = 1, [3] = 12}}
  CASES[#CASES + 1] = {"m_todo_t" .. t, "music.wav", {[1] = 1, [2] = t, [3] = 12}}
  for o = 0, 2 do
    CASES[#CASES + 1] = {"alias_7019_t" .. t .. "_os" .. o, "s7019_m6.wav", {[1] = 1, [2] = t, [3] = 9, [4] = 0, [22] = o}}
  end
  CASES[#CASES + 1] = {"alias18_7019_t" .. t .. "_os2", "s7019_m6.wav", {[1] = 1, [2] = t, [3] = 18, [4] = 0, [22] = 2}}
  CASES[#CASES + 1] = {"alias_3001_t" .. t .. "_os1", "s3001_m6.wav", {[1] = 1, [2] = t, [3] = 9, [4] = 0, [22] = 1}}
end
for p = 1, 23 do CASES[#CASES + 1] = {"preset" .. p, "music.wav", {[PRESET] = p}} end

reaper.Main_OnCommand(40859, 0) -- nueva pestaña
reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 48000, true)
reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.AddMediaItemToTrack(tr)
local take = reaper.AddTakeToMediaItem(item)
reaper.SetMediaItemInfo_Value(item, "D_POSITION", 0)
-- solo algunos casos: tests/out/only.txt con patrones separados por comas (REAPER no ve las variables de la terminal)
local of = io.open(OUT .. "/only.txt"); local only = of and of:read("l") or nil; if of then of:close() end

for _, c in ipairs(CASES) do
  local name, src, params = c[1], c[2], c[3]
  local sel = not only
  if only then for pat in only:gmatch("[^,]+") do if name:find(pat) then sel = true end end end
  if sel then
    local s = reaper.PCM_Source_CreateFromFile(ROOT .. "/signals/" .. src)
    reaper.SetMediaItemTake_Source(take, s)
    reaper.SetMediaItemInfo_Value(item, "D_LENGTH", math.min(reaper.GetMediaSourceLength(s), 30))
    reaper.SetMediaItemInfo_Value(item, "D_FADEINLEN", 0); reaper.SetMediaItemInfo_Value(item, "D_FADEOUTLEN", 0)
    reaper.UpdateItemInProject(item)
    while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
    local fx, info = -1, ""
    if c.chain then
      for _, f in ipairs(c.chain) do
        local k = reaper.TrackFX_AddByName(tr, f[1], false, -1)
        if k < 0 then log("ERROR no cargó", f[1]) break end
        for i, v in ipairs(f[2]) do reaper.TrackFX_SetParam(tr, k, i - 1, v) end
      end
    else
      fx = reaper.TrackFX_AddByName(tr, FX, false, -1)
      if fx < 0 then log("ERROR no cargó el FX") break end
      if params[PRESET] then reaper.TrackFX_SetParam(tr, fx, PRESET - 1, params[PRESET]) end
      for s_, v in pairs(params) do
        if s_ ~= PRESET then reaper.TrackFX_SetParam(tr, fx, s_ - 1, v) end
      end
    end
    local file = OUT .. "/" .. name .. ".wav"
    os.remove(file)
    reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true)
    reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
    reaper.GetSetProjectInfo(0, "RENDER_SRATE", 48000, true)
    reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
    reaper.GetSetProjectInfo(0, "RENDER_TAILFLAG", 0, true)
    reaper.GetSetProjectInfo_String(0, "RENDER_FORMAT", "ZXZhdyAAAQ==", true)   -- wav float 32 (sin recorte en 0 dBFS)
    reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true)
    reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
    reaper.Main_OnCommand(42230, 0)
    if fx >= 0 then
      local vals = {}
      for k = 1, 23 do local _, v = reaper.TrackFX_GetParam(tr, fx, k - 1); vals[#vals + 1] = string.format("%d=%g", k, reaper.TrackFX_GetParam(tr, fx, k - 1)) end
      info = table.concat(vals, " ")
    end
    log("caso", name, info)
  end
end
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_test.rpp", 0)
reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_test.rpp")
reaper.Main_OnCommand(40860, 0) -- cerrar pestaña
log("done")
logf:close()
