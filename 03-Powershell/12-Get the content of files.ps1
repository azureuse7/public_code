foreach ($gautam in $azureImages){
    $dockerfile=Get-Content -Path "images/$gautam"
    # Write-Host $dockerfile
}