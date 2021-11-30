# Self-elevate the script if required
if (-Not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {
 if ([int](Get-CimInstance -Class Win32_OperatingSystem | Select-Object -ExpandProperty BuildNumber) -ge 6000) {
  $CommandLine = "-File `"" + $MyInvocation.MyCommand.Path + "`" " + $MyInvocation.UnboundArguments
  Start-Process -FilePath PowerShell.exe -Verb Runas -ArgumentList $CommandLine
  Exit
 }
 }
write-host "Testing connection to Splunk deployment server..."
$testconnection = test-netconnection "Sample IP" -Port 8089 | select-Object TcpTestSucceeded
if($testconnection -match ".*True")
{
write-host "Connection to deployment server confirmed."
$Path = "c:\Splunk_Installer"
$FolderName = "Splunk_Installer"
$splunk_url = "https://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=windows&version=8.1.3&product=universalforwarder&filename=splunkforwarder-8.1.3-63079c59e632-x64-release.msi&wget=true"
$splunk_msi = "splunkforwarder-8.1.3-63079c59e632-x64-release.msi"
if (!(Test-Path $Path))
{
New-Item -ItemType Directory -Path "C:\" -Name $FolderName
}
else
{
write-host "Folder exists"
}
$install_path = "$Path\$splunk_msi"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -URI $splunk_url -outfile $install_path
cmd /c msiexec /i $install_path  /L "$Path\splunk_install_forwarder.log" AGREETOLICENSE=Yes DEPLOYMENT_SERVER="DS IP:Port" SPLUNKUSERNAME=splunk SPLUNKPASSWORD=goodPassword SERVICESTARTTYPE=auto LAUNCHSPLUNK=1 /quiet
exit
}
else 
{
write-host $testconnection
write-host "Connection to deployment server is missing.  Please establish a connection to <Enter IP>."
write-host "Waiting 15 seconds and then exiting..."
sleep(15)
exit
}