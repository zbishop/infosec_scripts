$name = query user $users /server:yourserver | select -skip 1
$session = $name -split " +", -2 | select -SkipLast 5 | select -skip 3
$session.ToString()
#$session = $session -replace "`t|`n|`r",""
$session.replace("`r|`n","") #| Set-content -Path C:\temp\test.txt 
logoff /server:yourserver $session
