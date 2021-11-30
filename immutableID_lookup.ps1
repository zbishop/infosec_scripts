$userUPN = Read-Host -Prompt "Input the User UPN (example: sally.smith@contoso.com)"
connect-msolservice

get-msoluser -UserPrincipalName $userUPN | select-object immutableid