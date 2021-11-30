write-host "Enter the base64 string"
$encodedCommand = Read-Host
$commandBytes = [System.Convert]::FromBase64String($encodedCommand)
$decodedCommand = [System.Text.Encoding]::Unicode.GetString($commandBytes)
print($decodedCommand)