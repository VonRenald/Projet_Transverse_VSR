# ProjetTrasverse Brice WEIS

## Index

+ [Introduction](#introduction)
+ [Ressources](#resources)
+ [Prerequis](#prerequis)
+ [Q0](#q0)
+ [Q1](#q1)
+ [Q2-3](#q2---q3)
+ [Q4](#q4)
+ [Ressource Autre](#ressource-autre)

## Introduction

Dans le cadre de la formation [SECIL](https://secil.univ-tlse3.fr/) du l'[Université Paul Sabatier](https://www.univ-tlse3.fr/),
nous avons pour objectif de produire des services contenus dans des Dockers devant être questionné par des clients. Le gestionnaire de charge a pour butte de créer, détruire et repartir le trafic entre les différents worker pour maintenir un temps de réponse suffisamment bas. 

## Resources 
[Sujet](https://docs.google.com/document/d/11zBVDOXcx6rLfGPptINeEuc0mywJ25OQWXOmVf0NwV4/edit#)

[Docker](https://docs.docker.com/engine/)

[TP Lavinal](https://www.irit.fr/~Emmanuel.Lavinal/cours/VSR/)

[TP Virtualisation](https://moodle.univ-tlse3.fr/pluginfile.php/620348/mod_resource/content/2/M2iLord-virtualization-TPs.pdf)

## Prerequis
### Installation Docker

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

### Installation SDK Docker
```
pip install docker
```


## Q0

treminal 1:

```
python3 worker.py
```

treminal 2:

```
python3 client.py
```

les deux programmes communiquent en local et sur le même port

## Q1

creation dockerfile



```
docker image build -t python:vsr .
```

## Q2 - Q3

### gestion_charge_V1

Repartie la charge des clients sur 3 docker créé à la main préalablement

---
### gestion_charge_V2
Repartie la charge des clients sur 3 docker créé au démarrage du programme et affiche le temps de réponse de chaque requête

## Q4

### gestion_charge_V3
Crée dynamiquement des docker si la latence dépasse un seuil défini à l'avance. Un docker est toujours en "sommeille" afin de rentrer en service dès que le besoin apparait, cela permet de ne pas à attendre le temps de démarrage du docker

la destruction des docker n'est pas implémenté,car des problèmes de libération des ports étaient présents

---
## gestion_cahrge_C

Version courante du programme, la création et la suppression dynamique des docker est correctement implémenté.

Mais le programme a pour défaut l'utilisation d'un nouveau port à chaque nouveau docker sans limitation, ce qui pourrait entraver le fonctionnement d'autre programme sur la même machine. Mais aussi les docker ouvert ne sont pas automatiquement fermés à la fin du programme

## Ressource Autre

arrêter tous les docker 

```
docker stop $(docker ps -q)
```
***
client V2   : envoie 1000 requête a la suite
***
Client End  : envoie un message ```quit```

