#It will delete all resources without asking any confirmation
Login-AzureRmAccount

$rgName = Get-AzureRmResourceGroup 

Foreach($name in $rgName)
{
Write-Host $name.ResourceGroupName
Remove-AzureRmResourceGroup -Name $name.ResourceGroupName -Verbose -Force
}