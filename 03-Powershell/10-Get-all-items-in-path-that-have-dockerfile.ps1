# Get-ChildItem filtered to paths that contain a Dockerfile
# Recursively lists all files named "Dockerfile" under a given path

$dockerfiles = Get-ChildItem -Path images/ -Recurse -File | Where-Object { $_.Name -eq "Dockerfile" }
Write-Host $dockerfiles
