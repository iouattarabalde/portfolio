' watch_reel_hidden.vbs
'
' Launcher shim for watch_reel_dropbox.ps1. Its only job is to start PowerShell
' with no visible console window.
'
' PowerShell's own -WindowStyle Hidden cannot do this. The console is allocated
' by Windows at process creation, before PowerShell parses the flag and hides
' it, so a scheduled task flashes a terminal for ~200ms on every tick. At a
' 5-minute interval that is 12 flashes an hour.
'
' WScript.Shell.Run passes SW_HIDE to CreateProcess itself, so the console is
' created hidden and never drawn. This is the only reliable fix on Windows.
'
' Registered by watch_reel_dropbox.ps1 -Setup. Not meant to be run by hand,
' though it is harmless if you do.

Option Explicit

Dim fso, shell, scriptDir, ps1, psExe, cmd, exitCode

Set fso   = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' Resolve the ps1 as a sibling of this file, so the pair can be moved or the
' repo re-cloned to another path without touching the scheduled task.
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
ps1       = fso.BuildPath(scriptDir, "watch_reel_dropbox.ps1")

If Not fso.FileExists(ps1) Then
    ' Nothing to log to, and no console to print to. A distinct exit code is the
    ' only signal available, and it surfaces in Task Scheduler's Last Run Result.
    WScript.Quit 2
End If

psExe = shell.ExpandEnvironmentStrings("%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe")

' -WindowStyle Hidden is deliberately absent: it is redundant here and its
' presence would imply it was doing the work, which it never was.
cmd = """" & psExe & """ -NoProfile -ExecutionPolicy Bypass -File """ & ps1 & """"

' 0 = hidden. True = wait for exit, which matters for two reasons: the task's
' Last Run Result stays meaningful instead of always reporting 0x0, and Task
' Scheduler's default "do not start a new instance" rule can actually see that a
' 25-minute encode is still running.
exitCode = shell.Run(cmd, 0, True)

WScript.Quit exitCode
