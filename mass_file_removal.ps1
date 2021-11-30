clear-content C:\temp\webServerQuery.txt
$computerlist= @(<'comma separated list of machines')
$filelist = @("files to remove")
foreach ($computer in $computerlist)
{
    Write-Host -ForegroundColor Yellow "Analysing $computer"
    #And for every file in the filelist
    foreach ($file in $filelist)
    {
                #We recreate the UNC filepath
                $newfilepath = Join-Path "\\$computer\" "$filelist"
                if (test-path $newfilepath)
                {
                    Write-Host "$newfilepath file exists"
                    try
                    {
                        #We try to remove...
                        Remove-Item $newfilepath -force -ErrorAction Stop
                    }
                    catch
                    {
                        #And there will be an error message if it fails
                        Write-host "Error while deleting $newfilepath on $computer.`n$($Error[0].Exception.Message)"
                        #We skip the rest and go back to the next object in the loop
                        continue
                    }
                    #if SUCCESS!!1!1! ...
                    Write-Host  "$newfilepath file deleted"
                }
    }

}