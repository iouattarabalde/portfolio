<#
.SYNOPSIS
    Drop-folder watcher for the hero reel. Run by a Scheduled Task every 5 min.

.DESCRIPTION
    Polls the drop folder for a new reel master and hands it to encode_reel.py.
    Everything real happens there; this is just the trigger, the log, and the
    Windows plumbing.

    The task is registered to run through watch_reel_hidden.vbs rather than
    powershell.exe directly. The shim exists purely to start PowerShell with no
    console window: -WindowStyle Hidden cannot do that, because Windows
    allocates the console before PowerShell ever sees the flag.

    Polling rather than a long-running FileSystemWatcher, deliberately: a
    scheduled poll survives reboots, sleep and Explorer restarts, can't leak a
    hung process, and a 5-minute delay is irrelevant next to a ~25 minute
    encode. encode_reel.py holds its own lock file, so ticks that land during a
    run exit immediately instead of starting a second encode.

    A run that reaches the review gate BLOCKS here until a CRF is picked (in the
    browser page it opens, or via --pick), up to encode_reel.py's timeout. That
    is intentional -- it keeps the lock held so no second master jumps the queue.

.PARAMETER Setup
    Registers the Scheduled Task and creates the drop folder, then exits.

.PARAMETER Unregister
    Removes the Scheduled Task.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\watch_reel_dropbox.ps1 -Setup
#>
[CmdletBinding()]
param(
    [switch]$Setup,
    [switch]$Unregister
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir
$Encoder   = Join-Path $ScriptDir 'encode_reel.py'
$LogFile   = Join-Path $ScriptDir 'reel-encode.log'   # *.log is gitignored
$TaskName  = 'IOB-ReelEncoder'

# Keep in step with DROP_DIR in encode_reel.py; REEL_DROP_DIR overrides both.
$DropDir = if ($env:REEL_DROP_DIR) { $env:REEL_DROP_DIR } else { 'E:\_reel-dropbox' }

function Write-Log {
    param([string]$Message, [string]$Level = 'INFO')
    $line = '{0} [{1}] {2}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Level, $Message
    Add-Content -LiteralPath $LogFile -Value $line -Encoding utf8
    Write-Host $line
}

function Rotate-Log {
    # A scheduled task that fails silently is worse than no task at all, so the
    # log is the only real feedback channel. Keep it from growing without bound.
    if (Test-Path $LogFile) {
        $sizeMB = (Get-Item $LogFile).Length / 1MB
        if ($sizeMB -gt 5) {
            Move-Item -LiteralPath $LogFile -Destination "$LogFile.1" -Force
        }
    }
}

function Resolve-Python {
    foreach ($candidate in @('python', 'python3', 'py')) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    throw 'No Python interpreter found on PATH.'
}

# ---------------------------------------------------------------------------
# Setup / teardown
# ---------------------------------------------------------------------------

if ($Setup) {
    if (-not (Test-Path $DropDir)) {
        New-Item -ItemType Directory -Path $DropDir -Force | Out-Null
        Write-Host "Created drop folder: $DropDir"
    } else {
        Write-Host "Drop folder already exists: $DropDir"
    }

    # The \" escaping is required, not cosmetic: both paths contain spaces, and
    # PowerShell 5.1 strips bare double quotes when handing arguments to a native
    # exe -- schtasks then sees "Code\portfolio\..." as a separate argument and
    # rejects it. Escaped quotes survive the handoff intact.
    #
    # wscript.exe rather than powershell.exe directly. -WindowStyle Hidden does
    # not prevent the console from being drawn: Windows allocates it before
    # PowerShell can act on the flag, so the task flashed a terminal on every
    # tick. The shim passes SW_HIDE at process creation, which does work.
    $wscript = Join-Path $env:SystemRoot 'System32\wscript.exe'
    $shim    = Join-Path $ScriptDir 'watch_reel_hidden.vbs'
    if (-not (Test-Path $shim)) {
        throw "Launcher shim missing: $shim"
    }
    $cmd = '\"{0}\" \"{1}\"' -f $wscript, $shim

    # schtasks.exe rather than Register-ScheduledTask, for two concrete reasons
    # found the hard way: the cmdlets need elevation to write a task at the root
    # folder, and their "repeat forever" TimeSpan ([TimeSpan]::MaxValue) is
    # accepted by New-ScheduledTaskTrigger but then REJECTED by Task Scheduler as
    # out of range. /SC MINUTE /MO 5 expresses the same thing natively and
    # registers fine as a normal user.
    #
    # No /RU or /RL: the task runs as the invoking user, only while logged on.
    # That is deliberate -- the review gate opens a browser page, which needs a
    # desktop session to open onto.
    $out = schtasks /Create /SC MINUTE /MO 5 /TN $TaskName /TR $cmd /F 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host $out
        throw "Could not register the scheduled task (exit $LASTEXITCODE)."
    }

    Write-Host ''
    Write-Host "Registered scheduled task '$TaskName' (every 5 minutes)."
    Write-Host "Drop a reel master into: $DropDir"
    Write-Host "Log: $LogFile"
    Write-Host ''
    Write-Host "Remove it later with:  -Unregister"
    exit 0
}

if ($Unregister) {
    schtasks /Delete /TN $TaskName /F | Out-Null
    Write-Host "Removed scheduled task '$TaskName'."
    exit 0
}

# ---------------------------------------------------------------------------
# Normal tick
# ---------------------------------------------------------------------------

# The tick runs unattended behind the shim: no console, nobody watching. An
# unhandled terminating error would exit silently and leave the log ending
# mid-sentence -- which is exactly how the stderr bug below hid itself for so
# long. Catch anything that gets this far and write down why.
try {
    Rotate-Log

    if (-not (Test-Path $DropDir)) {
        Write-Log "Drop folder missing: $DropDir. Run with -Setup." 'ERROR'
        exit 1
    }

    $exts = @('.mov', '.mp4', '.mxf', '.m4v', '.avi', '.mkv')
    $pending = Get-ChildItem -LiteralPath $DropDir -File -ErrorAction SilentlyContinue |
        Where-Object { $exts -contains $_.Extension.ToLower() }

    if (-not $pending) { exit 0 }   # quiet tick, nothing to say

    try {
        $python = Resolve-Python
    } catch {
        Write-Log $_.Exception.Message 'ERROR'
        exit 1
    }

    Write-Log ("Tick: {0} candidate file(s) in drop folder." -f $pending.Count)

    # encode_reel.py decides what's actually new (its own state file), waits for
    # the file to finish copying, and no-ops if another run holds the lock.
    #
    # $ErrorActionPreference has to drop to Continue across this one call.
    # PowerShell 5.1 wraps every stderr line from a native command in an
    # ErrorRecord, and 2>&1 feeds those into the pipeline; under 'Stop' the
    # first one becomes a TERMINATING NativeCommandError. The script died right
    # there -- before the $LASTEXITCODE check below, and before the offending
    # stderr line was even written -- so a failed encode logged its last stdout
    # line and then nothing: no traceback, no exit code, no 'Tick complete.'
    # Python writes its traceback to stderr, which is the single most useful
    # thing that can land in this log. Here stderr is output to record, not an
    # exception to raise on.
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $python $Encoder --watch 2>&1 | ForEach-Object {
            Add-Content -LiteralPath $LogFile -Value "$_" -Encoding utf8
            Write-Host $_
        }
    } finally {
        $ErrorActionPreference = $prevEap
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Log "encode_reel.py exited with code $LASTEXITCODE." 'ERROR'
        exit $LASTEXITCODE
    }

    Write-Log 'Tick complete.'
}
catch {
    # Write-Log can itself be what broke (an unwritable or locked log file), so
    # it gets its own guard. Failing that, the exit code is the last signal
    # left: Task Scheduler shows it as Last Run Result, and task history is on.
    try {
        Write-Log ("Unhandled error: {0}: {1}" -f `
                   $_.Exception.GetType().Name, $_.Exception.Message) 'ERROR'
        $pos = $_.InvocationInfo.PositionMessage
        if ($pos) { Write-Log ("  {0}" -f $pos.Trim()) 'ERROR' }
    } catch { }
    exit 1
}
