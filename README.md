# Description
Yatube is blog-site with opportunity: 
  * register and authentiticate
  * create personal or group post with pictures, edit and delete them 
  * subscribe/unsubscribe other users and groups, that allow you to see only their posts
  * create, edit and delete comment on posts page

# Installation:
## 1) For local usage:
Clone repository:
```
git clone https://github.com/Mackleroy/Yatube.git
```
Install Docker and Docker-compose as is said in official guide: https://docs.docker.com/engine/install/

Come in root directory of project
```
cd Yatube/
```
Make .env from .env*example with your personal data

Then use
```
sudo docker-compose -f docker-compose.local.yaml up --build
```

## 2) For web-server usage:
Clone repository on your machine:
```
git clone https://github.com/Mackleroy/Yatube.git
```
Install Docker and Docker-compose as is said in official guide: https://docs.docker.com/engine/install/

Come in root directory of project
```
cd Yatube/
```
Make .env from .env*example with your personal data

Then use
```
sudo docker-compose -f docker-compose.prod.yaml up --build
```
To activate Docker, list of all availiable containers 
```
sudo docker ps
```
Find yatube_web_1 container

Come into Django-Project container 
```
sudo docker exec -it <yatube_web_1 container's ID> sh
```
Configure it like a local project, migrate tabeles for PostgreSQL and collectstatic
```
python3 manage.py migrate
python3 manage.py collectstatic
```
