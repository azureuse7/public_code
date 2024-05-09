# How to Execute Commands in a Running Container

For this, you'll have to use the exec command to execute a custom command inside a running container.

The generic syntax for the exec command is as follows:
```bash
docker container exec <container identifier> <command>
```
To execute npm run db:migrate inside the notes-api container, you can execute the following command:
```bash
docker container exec notes-api npm run db:migrate

# > notes-api@ db:migrate /home/node/app
# > knex migrate:latest
#
# Using environment: production
# Batch 1 run: 1 migrations
```
In cases where you want to run an interactive command inside a running container, you'll have to use the -it flag. As an example, if you want to access the shell running inside the notes-api container, you can execute following the command:
```bash
docker container exec -it notes-api sh
```
# / # uname -a
# Linux b5b1367d6b31 5.10.9-201.fc33.x86_64 #1 SMP Wed Jan 20 16:56:23 UTC 2021 x86_