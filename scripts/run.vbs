Set oShell = CreateObject ("Wscript.Shell")
Dim strArgs
strArgs = "cmd /c python kate-abstract-python"
oShell.Run strArgs, 0, false
