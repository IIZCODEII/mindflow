<div align='center'  ><img width=200px height=200px src="img_notebook/mindflow.png"></div>

# MindFlow : Reconnaisance d'emotions en temps réel.

L'idée de notre projet est de proposer une application permettant de detecter les emotions cardinales en temps réel sur un flux vidéo webcam. L'objectif est d'apporter une contribution positive pour le diagnostic des problèmes de santé mentale sur les plateformes de streaming en ligne type Twitch.

Dans cette visée d'être le plus utile et pratique possible, nous avons orienter notre travail sur la production d'une *proof-of-concept* concrète.


## Concept et UI

![UI](img_notebook/mindflow_ui.png)

La figure ci-dessus met en évidence l'interface utilisateur qui est née de cette recherche. Elle met en avant la necessité de ne pas se contenter des prédictions du modèle de reconnaissance et de restituer des statististiques *live* et sur l'ensemble de la session permettant de pointer vers un pré-diagnostic ( par exemple profil emotionel de la personne sur la session, part des émotions négatives etc).

Pour materialiser cette ambition, il faut composer avec deux impératifs:

* Bonne qualité des prédictions
* Faible temps d'inference

C'est avec ces contraintes en tête que nous avons articuler conceptuelement les différentes briques de MindFlow

## Workflow

![conceptual_wf](img_notebook/video_feed_workflow.png)

### Face Detection Algorithm : Haar-Viola-Jones

Choix d'une approche directe type Haar-Viola-Jones plutot que Deep Learning pour les raisons suivantes :

* Temps de latence réduit
* Pas de temps passé à optimiser et à entrainer le modèle
* Utilisé et eprouvé dans l'industrie depuis des decennies sur les equipements photos et vidéos

En particulier, l'algorithme de Haar-Viola-Jones permet de traiter au moins 15 images par secondes en moyenne et a été la première methode permettant la detection d'objet en temps réel.

![haar](img_notebook/img9.png)


* La méthode de Viola et Jones permet la reconnaissance faciale en discrétisant une image à l’aide d’une série de rectangles adjacents. Pour chacun d’eux, il faut calculer l’intensité moyenne des pixels qui s’y trouvent. On définit alors les caractéristiques pseudo-Haar, qui sont calculées par la différence des sommes de pixels de deux ou plusieurs zones rectangulaires adjacentes. 

* Nous allons procéder de façon similaire en changeant l’échelle de la décomposition de l’image et donc travailler sur des rectangles de plus en plus grands. Viola et Jones prennent ainsi un facteur multiplicatif de 1,25 à chaque changement d’échelle, jusqu'à ce que la fenêtre couvre la totalité de l'image.

* Ils utilisent ensuite un algorithme de boosting, adapté d’AdaBoost.  Ce classificateur dit fort utilise la combinaison optimale de classificateurs faibles tels que des arbres de décision : il prend en compte à chaque nouvelle itération un nouveau classificateur faible. 

* Cette méthode risque d’induire une grande complexité du fait du fait des différents changements d’échelle. Viola et Jones introduisent la méthode dite des « cascades des classifieurs (ou classificateurs) » pour éviter les calculs inutiles et réduire la complexité. Ils veulent être capables d’identifier les zones où l’objet recherché ne se trouve vraisemblablement pas, les extraire du champ spatial d’investigation ai ainsi mieux se concentrer sur les parties de l’image où il a une probabilité non négligeable de se trouver. En  partant des classificateurs les plus simples lorsqu’on construit l’algorithme de boosting, on peut rejeter très rapidement la grande majorité des exemples négatifs.

## Face Emotion Recognition Model

![iter](img_notebook/iter_fer.png)

Deux notebooks disctincts présent dans le dépot décrivent notre approche pour les deux itérations effectuées sur le modèle de FER.

Principaux résultats de ces itérations:

1. Acc ~56%, F1 Score 50% : prb de données => grayscale, definition trop basse, émotions caricaturales, methodes de scraping => label peu pertinent, beaucoup d'intersections, unbalanced data
2. Acc ~62%, meilleure architecture et données cependant toujours les mêmes problemes de labelisations que sur la première iteration 

Il est important de se rendre compte que ces métriques ne seront jamais completement revalatrices des vrais performances du FER model, l'inference se fait sur des données différentes que celles sur lesquelles le modèle est entrainé (stream webcam) et nous n'avons pas de quoi evaluer la performance sur les données strictes de notre cas d'usage.
Les distributions sont différentes ( problème des datasets crowdsourcé/scrappé) meme si globalement les similarités permettent de rendre le FER model exploitable dans le cadre de cette POC.


## Workflow logiciel

![iter](img_notebook/wf_mind.png)

## Lancer le projet

1. Télécharger le modèle DAN préentrainé ici https://drive.google.com/file/d/1uHNADViICyJEjJljv747nfvrGu12kjtu/view?usp=sharing et le mettre dans le répertoire app/models
2. Build une image docker avec le dockerfile ou simplement installer les requierments via pip
3. Executer la commande suivante à la racine du dépôt : `python app/server.py serve`


```python

```
