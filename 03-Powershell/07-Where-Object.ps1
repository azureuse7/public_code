# The Where-Object cmdlet can be piped behind any cmdlet in PowerShell to select (filter)

Get-Service | Where-Object -Property Status -eq "Running"


Get-Service | Where-Object Status -eq "Running"
# Or even:
Get-Service | ? Status -eq "Running"


Get-Service | Where-Object {($_.Status -ne "Running") -and ($_.StartType -eq 'Automatic')}