$subs = wecutil es
foreach ($sub in $subs) {
wecutil gr $sub #> c:\temp\wecutil_test.txt
}

#wecutil gr "GV_PowerShell"
#wecutil gr "GV_Security"
#wecutil gr "GV_System&Application"
#wecutil gs "GV_PowerShell"
#wecutil gs "GV_Security"
#wecutil gs "GV_System&Application"
#Get-ChildItem C:\wecutil_runtime_outputs\*.* | Rename-Item -NewName {$_.Name -replace '.txt', ((get-date).ToString("yyyyMMdd_HH_mm_ss")+".txt")}
#Start-Sleep -Seconds 60
#Get-ChildItem C:\wecutil_runtime_outputs\*.* | Remove-Item -Force