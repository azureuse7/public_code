# The Select-Object cmdlet is always piped behind another cmdlet in PowerShell. 
# It allows you to select or modify properties from objects that come down the pipeline.

Get-Process | Select-Object -Property Name, CPU