Set WshShell = CreateObject("WScript.Shell")
' Launch backend (hidden)
WshShell.Run "run_backend.bat", 0, False
' Wait 2 seconds for server
WScript.Sleep 2000
' Launch frontend (normal window)
WshShell.Run "run_frontend.bat", 0, False
