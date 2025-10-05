# New-AzResourceGroup -Name rg-dev-uks-gagan-registry -Location Uksouth

#  Check if ACR exists
$acr = az acr check-name -n singh1 | convertfrom-json

if($acr.nameAvailable -match "True"){
    az acr create -n singh1 -g gagan --sku Standard
} else {
    write-host ("acr exists" )
}

#  Check if image exists
$tfVersion= "1.0.5"
$availableTags = az acr repository show --name singh1 --image gagan:$tfVersion | convertfrom-json


if($availableTags.name -match $tfVersion){
    write-host ("Latest terraform version exists")
}else{

    az acr login --name singh1
    docker build -t gagan:$tfVersion .
    docker tag gagan:$tfVersion singh1.azurecr.io/ggagan$tfVersion
    docker push singh1.azurecr.io/gagan:$tfVersion
}


    # Build the terratest docker container
    # - script: |
    #   docker build $(Agent.BuildDirectory)${{ parameters.testFileSource }}/.pipelines/test-runner -t terratest:local --build-arg tfVersion=${{ parameters.tfVersion }}
    #   displayName: Build terratest container
