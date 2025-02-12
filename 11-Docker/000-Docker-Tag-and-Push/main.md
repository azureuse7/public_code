https://www.middlewareinventory.com/blog/deploy-docker-image-to-kubernetes/#google_vignette

#### Create a docker repo in docker hub calls it "auth"


```bash
docker build .

docker images

docker tag f5813f4913bd44e0006d823whatevertheidis gaganvthakur/auth:latest

docker login 

docker push gaganvthakur/auth:latest
```

#### Working with Container Registry (Azure Container Registry)
- Create a new Azure Container Registry (ACR) in Azure portal.

- Enable *Admin* credentials from ACR.

- Login to ACR:

```bash
$acrName="myacr"
az acr login -n $acrName --expose-token
```

- Build the image on ACR (Optional):

```bash
az acr build -t "$acrName.azurecr.io/webapp:1.0" -r $acrName .
```

- Note that image is already pushed to ACR.
