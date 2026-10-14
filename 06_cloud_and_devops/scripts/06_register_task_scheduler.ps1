# =====================================================================
# 06_register_task_scheduler.ps1
# Run from: Windows PowerShell (administrator recommended)
# Purpose: Registers a daily Windows Task Scheduler job that wakes WSL2
#          (if needed) and runs 05_backup.sh inside it.
#
# Why Windows Task Scheduler instead of cron inside WSL:
#   When WSL2 is fully shut down, any cron daemon running inside it stops
#   too. Windows Task Scheduler calling wsl.exe directly will wake WSL2
#   at the scheduled time, run the script, and let it go back to idle
#   afterward.
#
# Note: Comments are in English on purpose - Windows PowerShell 5.1 can
#       misinterpret non-ASCII (Korean) characters in a .ps1 file if the
#       encoding isn't exactly right, which can silently break variable
#       assignments. Keeping this file ASCII-only avoids that entirely.
#
# Usage: Edit $WslDistro and $WslUser below to match your environment,
#        then run this script. Check your distro name with: wsl -l -v
# =====================================================================
 
$WslDistro = "Ubuntu"          # exact distro name from `wsl -l -v`
$WslUser   = "ros2-server"     # WSL Linux username
$TaskName  = "LimoCapstoneBackup"
$RunTime   = "23:00"           # daily run time (24h format)
 
# NOTE: the backup script itself lives at ~/limo_ws/backup.sh inside WSL
# (it's a symlink to ~/scripts/05_backup.sh - see 05_backup.sh header).
$action = New-ScheduledTaskAction `
    -Execute "wsl.exe" `
    -Argument "-d $WslDistro -u $WslUser -e bash -c '~/limo_ws/backup.sh'"
 
$trigger = New-ScheduledTaskTrigger -Daily -At $RunTime
 
# -WakeToRun        : try to wake the laptop from sleep to run the task
#                      (actual behavior depends on laptop power settings)
# -StartWhenAvailable: if the laptop was off at the scheduled time, run
#                      the missed task as soon as it's next available
$settings = New-ScheduledTaskSettingsSet `
    -WakeToRun `
    -StartWhenAvailable `
    -DontStopOnIdleEnd
 
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Daily backup of LIMO capstone simulation results to Oracle Cloud"
 
Write-Host "Task registered: $TaskName (runs daily at $RunTime)"
Write-Host "To test immediately: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "To check the log afterward, run inside WSL: cat ~/limo_ws/backup.log"
 