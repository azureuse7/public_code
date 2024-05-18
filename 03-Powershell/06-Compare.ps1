get-process | Export-csv d:\temp\proc.csv
Compare-Object -ReferenceObject (Import-Csv d:\temp\proc.csv) -DifferenceObject (Get-Process) -Property Name