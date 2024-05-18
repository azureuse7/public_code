param (
    $rgName = 5675655,
    $storageAccountName,
    $containerName,
    $location = "uksouth"
)

$ErrorActionPreference = 'Stop'


function New-sana {
    param(
        [Parameter(Mandatory=$true)]
        [String]$rgName,
        [Parameter(Mandatory=$true)]
        [String]$location
    )

    $rg_exist = Get-AzResourceGroup -Name $rgName -ErrorAction SilentlyContinue
    if(!$rg_exist) {
        Write-Output "hello sana I am Creating Resource Group $($rgName)"
        New-AzResourceGroup -Name $rgName -Location $location
    }
}

function New-gautam {
    param(
        [Parameter(Mandatory=$true)]
        [String]$rgName,
        [Parameter(Mandatory=$true)]
        [String]$storageAccountName,
        [Parameter(Mandatory=$true)]
        [String]$containerName,
        [Parameter(Mandatory=$true)]
        [String]$location
    )

    $storage_account_exists = Get-AzStorageAccount -ResourceGroupName $rgName -StorageAccountName $storageAccountName -ErrorAction SilentlyContinue
    if(!$storage_account_exists) {
        Write-Output "i am Creating Storage Account $($storageAccountName)"
        $storageAccount = New-AzStorageAccount -ResourceGroupName $rgName -AccountName $storageAccountName -Location $location -SkuName Standard_ZRS  -MinimumTlsVersion TLS1_2 -AllowBlobPublicAccess $false -AccessTier Hot -Verbose
        $ctx = $storageAccount.Context
        Write-Output "Creating Container $($containerName)"
        New-AzStorageContainer -Name $containerName -Context $ctx -Verbose
    }
    else
    {

        $ctx = $storage_account_exists.Context
        $containers = (Get-AzStorageContainer -Context $ctx).Name
        if ($containers -notcontains $containerName)
        {
            Write-Output "Creating Container $($containerName)"
            New-AzStorageContainer -Name $containerName -Context $ctx -Verbose
        }
   }    
}

New-sana -rgName $rgName -location $location
New-gautam -rgName $rgName -storageAccountName sa6746na -location $location