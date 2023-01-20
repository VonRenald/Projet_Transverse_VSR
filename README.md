# ProjetTrasverse Brice WEIS


## resource 
[sujet](https://docs.google.com/document/d/11zBVDOXcx6rLfGPptINeEuc0mywJ25OQWXOmVf0NwV4/edit#)

[docker](https://docs.docker.com/engine/)

[TP_Lavinal](https://www.irit.fr/~Emmanuel.Lavinal/cours/VSR/)

[TP](https://moodle.univ-tlse3.fr/pluginfile.php/620348/mod_resource/content/2/M2iLord-virtualization-TPs.pdf)


## install docker

```
sudo apt-get update

sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

sudo mkdir -p /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo chmod a+r /etc/apt/keyrings/docker.gpg
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```


## Q1

treminal 1:

```
python3 worker.py
```

treminal 2:

```
python3 client.py
```

## Q2

creation dockerfile



```
docker image build -t python:vsr .
```

stop all docker

```
docker stop $(docker ps -q)
```


```
creation de docker dinamique -> ok
destruction doquer dinamique -> erreur, probleme de binbing. garder en memeoir le dernier port utiliser pour en creer un apres
```