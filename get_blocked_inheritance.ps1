$blockedOUs=Get-ADorganizationalunit -Filter * | Get-GPInheritance | where-object gpoinheritanceblocked
write-host $blockedOUs
clear-content c:\temp\gpo_inheritance_objects.txt
clear-content C:\temp\blocked_ous.txt
$OUs=Get-ADorganizationalunit -Filter * | Get-GPInheritance | Where-Object {($_.GpoLinks -notmatch 'InfoSec WEF/Audit GPO') -and ($_.InheritedGpoLinks -notmatch 'InfoSec WEF/Audit GPO')} | Select-Object -expandproperty Path | Add-Content C:\temp\blocked_OUs.txt | write-host
$OUpath=Get-content "C:\temp\blocked_OUs.txt"
ForEach ($line in $OUpath) 
{
$blockedObject=(Get-ADcomputer -Filter * -SearchBase $line)
Add-Content c:\temp\blocked_inheritance_objects.txt $blockedObject
write-host $blockedObject
}