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
Create virtual environment and activate it
```
python3 -m venv venv
source venv/bin/activate
```
Install all dependencies 
```
pip install -r requirements.txt
```
Then come in root derictory of project and apply regular configurations
```
python3 manage.py makemigratons
python3 manage.py migrate
```
Start server
```
python3 manage.py runserver
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
Then use
```
sudo docker-compose up --build
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
