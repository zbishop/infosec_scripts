#New-Item -Path 'C:\' -Name "wecutil_outputs\" -ItemType "Directory"
wecutil gr GV_PowerShell > 'C:\wecutil_runtime_outputs\gv_powershell_runtime.txt'
wecutil gr GV_Security > 'C:\wecutil_runtime_outputs\gv_Security_runtime.txt'
wecutil gr "GV_System&Application" > 'C:\wecutil_runtime_outputs\gv_system&application_runtime.txt'
wecutil gs GV_PowerShell > 'C:\wecutil_subscription_outputs\gv_powershell_Status.txt'
wecutil gs GV_Security > 'C:\wecutil_subscription_outputs\gv_Security_Status.txt'
wecutil gs "GV_System&Application" > 'C:\wecutil_subscription_outputs\gv_system&application_Status.txt'
#Get-ChildItem C:\wecutil_runtime_outputs\*.* | Rename-Item -NewName {$_.Name -replace '.txt', ((get-date).ToString("yyyyMMdd_HH_mm_ss")+".txt")}
#get-childitem C:\wecutil_runtime_outputs\*.* | Copy-Item -Destination \\tsclient\c\temp\wecutil_runtime_outputs -Force
#Start-Sleep -Seconds 60
#Get-ChildItem C:\wecutil_runtime_outputs\*.* | Remove-Item -Force