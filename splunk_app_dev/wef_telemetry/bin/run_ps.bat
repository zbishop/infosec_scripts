@ECHO OFF

set SplunkApp=wef_telemetry
set SPLUNK_HOME=C:\Program Files\SplunkUniversalForwarder

%SystemRoot%\system32\WindowsPowerShell\v1.0\powershell.exe -executionPolicy unsigned -command "'%SPLUNK_HOME%\etc\apps\%SplunkApp%\bin\wec_subscriptions_runtime.ps1'"
