https://www.youtube.com/watch?v=B9uaQcc2dLs&list=WL&index=4&ab_channel=TechnoPanti


1) touch abc.txt 
2) vim gautam (save this)
3) ls -> location of the file is home/gautam/abc.txt 

4) docker run -d -volume home/gautam/abc.txt:/temp <image id> sleep infinity

/temp is folder inside the container 

5) docker exec -it <image id>
6) cd /temp 
7)  cat abc.txt 

also
docker container run \
    --rm \
    --publish 3000:3000 \
    --name hello-dock-dev \
    --volume $(pwd):/home/node/app \
    hello-dock:dev


How would we do that in docker compose file 

```bash
  python: #docker run --rm -it -v ${PWD}:/work -w /work -p 5003:5000 aimvector/python:1.0.0 /bin/sh
    container_name: python
    image: aimvector/python:1.0.0
    build:
      context: ./python
      target: debug
    #working_dir: /work      #comment out for build.target:prod
    #entrypoint: /bin/sh     #comment out for build.target:prod
    #stdin_open: true        #comment out for build.target:prod
    #tty: true               #comment out for build.target:prod
    volumes:
    - ./11-Docker/01_docker_dotnet/:/work  # local source, create a file here 
    ports:
      - 5003:5000
      - 5678:5678
```

```bash
docker-compose up -d # how to build 
docker ps # 
docker exec it -python sh # how to enter the container 
```