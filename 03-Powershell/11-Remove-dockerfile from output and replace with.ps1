# Remove "Dockerfile" from file path strings and replace with an image tag
# Useful when generating Docker image names from directory paths

$files = Get-ChildItem -Path images/ -Recurse -File -Name | Where-Object { $_ -match "Dockerfile" }

foreach ($file in $files) {
    # Replace the "Dockerfile" segment with a target image tag
    $imageName = $file.Replace("/Dockerfile", "").Replace("\Dockerfile", "").Replace("/", "-")
    Write-Host "Image name: $imageName"
}
