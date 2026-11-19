-- CPU: 10 instancias en cada configuracion, render de 60 s del premaster de Nube baja. Escribe tests/out/perf.txt
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local AUDIO = os.getenv("HOME") .. "/Music/ClaudeBeats/Mezcla/nube_baja_mezcla_premaster_X20.wav"
os.execute('mkdir -p "' .. OUT .. '"')
local f = io.open(OUT .. "/perf.txt", "w")
reaper.Main_OnCommand(40859, 0)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.AddMediaItemToTrack(tr); local take = reaper.AddTakeToMediaItem(item)
reaper.SetMediaItemTake_Source(take, reaper.PCM_Source_CreateFromFile(AUDIO))
reaper.SetMediaItemInfo_Value(item, "D_LENGTH", 60)
local function render(name, nfx, params)
  while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
  for k = 1, nfx do
    local fx = reaper.TrackFX_AddByName(tr, "JS:Nube Satura/nube_satura.jsfx", false, -1)
    for p, v in pairs(params) do reaper.TrackFX_SetParam(tr, fx, p - 1, v) end
  end
  os.remove(OUT .. "/" .. name .. ".wav")
  reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true); reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
  reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true); reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
  local t0 = reaper.time_precise(); reaper.Main_OnCommand(42230, 0); return reaper.time_precise() - t0
end
local t0 = render("perf_vacio", 0, {})
local cfg = {
  {"sub, sin OS", {[22] = 0}}, {"sub, 4x", {[22] = 1}}, {"saturar todo, duro, 4x", {[1] = 1, [2] = 3, [22] = 1}},
  {"saturar todo, valvula, 8x", {[1] = 1, [2] = 2, [22] = 2}},
  {"radio + lo-fi + crujiente, 8x", {[1] = 2, [22] = 2, [18] = 8, [19] = 2.5, [20] = -10}},
}
f:write(string.format("sin plugin %.2f s\n", t0))
for i, c in ipairs(cfg) do
  local t = render("perf_" .. i, 10, c[2])
  f:write(string.format("%-32s %.2f %% de un nucleo por instancia\n", c[1], (t - t0) / 60 / 10 * 100))
end
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_perf.rpp", 0); reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_perf.rpp"); reaper.Main_OnCommand(40860, 0)
f:write("done\n"); f:close()
