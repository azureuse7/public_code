foreach ($gagan in $azureImages){
    $dockerfile=Get-Content -Path "images/$gagan"
    # Write-Host $dockerfile
}