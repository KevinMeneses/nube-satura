-- Abre una pestaña de demo: pista con 20 s del premaster de Nube baja (fader en -inf, no suena), Nube Satura con un preset,
-- ventana del FX flotante y reproducción en loop para ver las gráficas. Cerrar con tests/ui_close.lua.
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
-- opciones (REAPER no ve las variables de la terminal): tests/out/demo_opts.txt = "preset empuje"
local o = io.open(ROOT .. "/out/demo_opts.txt"); local OPTS = {}
if o then for w in o:read("a"):gmatch("%S+") do OPTS[#OPTS + 1] = tonumber(w) end o:close() end
local AUDIO = ROOT .. "/signals/music.wav"
reaper.Main_OnCommand(40859, 0)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "Nube Satura demo", true)
reaper.SetMediaTrackInfo_Value(tr, "D_VOL", 0)
local item = reaper.AddMediaItemToTrack(tr); local take = reaper.AddTakeToMediaItem(item)
local src = reaper.PCM_Source_CreateFromFile(AUDIO); reaper.SetMediaItemTake_Source(take, src)
reaper.SetMediaItemInfo_Value(item, "D_LENGTH", reaper.GetMediaSourceLength(src))
reaper.UpdateArrange()
local fx = reaper.TrackFX_AddByName(tr, "JS:Nube Satura/nube_satura.jsfx", false, -1)
reaper.TrackFX_SetParam(tr, fx, 23, OPTS[1] or 4)
if OPTS[2] then reaper.TrackFX_SetParam(tr, fx, 2, OPTS[2]) end
reaper.TrackFX_Show(tr, fx, 3)
reaper.GetSet_LoopTimeRange(true, true, 0, reaper.GetMediaSourceLength(src), false)
reaper.SetEditCurPos(0, false, false)
reaper.GetSetRepeat(1)
reaper.OnPlayButton()
local f = io.open(ROOT .. "/out/ui.txt", "w"); f:write("done\n"); f:close()
