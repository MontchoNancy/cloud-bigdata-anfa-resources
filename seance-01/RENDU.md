# Rendu Séance 1

**Nom et prénom :** Nancy Montcho
**Identifiant GitHub :** MontchoNancy

## Résumé de la séance

Cette première séance pose la première brique d'infrastructure du projet Anfa : un service de stockage objet. J'ai déployé MinIO en local avec Docker, qui expose une API compatible S3 — la même API que celle utilisée par Amazon S3 en production. Cela illustre concrètement l'intérêt de l'open source pour la portabilité : le code écrit pour MinIO fonctionnerait quasiment à l'identique sur AWS S3, GCP ou tout autre fournisseur compatible S3, en ne changeant que l'URL de l'endpoint et les identifiants.

J'ai ensuite créé le bucket `anfa-raw`, destiné à recevoir les données brutes du projet, puis une paire de clés applicatives (`anfa-app-key` / `anfa-app-secret-2026`) distincte des identifiants root du serveur. Cette séparation entre compte administrateur et compte de service applicatif est une bonne pratique de sécurité : elle limite les dégâts en cas de fuite des clés applicatives puisqu'elles n'ont pas le pouvoir total sur le système. Enfin, j'ai écrit un script Python qui utilise `boto3` pour vérifier l'existence du bucket, uploader les 4 fichiers CSV du référentiel (lignes, arrêts, bus, tarifs) et lister le contenu du bucket pour confirmer l'opération.

## Étapes principales

1. Vérification de l'environnement : `docker --version` et `docker compose version` répondent correctement, confirmant que Docker Desktop est fonctionnel.
2. Fork du dépôt `cloud-bigdata-anfa-resources` sur mon compte GitHub personnel.
3. Clone du fork en local, puis création de la branche `seance-01` avec `git checkout -b seance-01`.
4. Création du dossier `seance-01/` à la racine du dépôt.
5. Téléchargement de l'image MinIO (`docker pull minio/minio`) puis lancement d'un conteneur `anfa-minio` exposant les ports 9000 (API S3) et 9001 (console web), avec un volume nommé `anfa-minio-data` pour la persistance.
6. Vérification du conteneur via `docker ps` (statut `Up`, ports visibles).
7. Connexion au conteneur (`docker exec -it anfa-minio sh`) pour administrer MinIO avec `mc` :
   - Configuration d'un alias `local` pointant vers `http://localhost:9000`.
   - Création du bucket `anfa-raw` avec `mc mb local/anfa-raw`.
   - Création d'une clé applicative dédiée (`anfa-app-key` / `anfa-app-secret-2026`) via
     `mc admin user svcacct add`, distincte des identifiants root.
8. Mise en place de l'environnement Python : création d'un environnement virtuel `.venv`, installation de `boto3` via `requirements.txt`.
9. Écriture du script `upload_referentiel.py` qui vérifie l'accessibilité du bucket, uploade les 4 CSV du dossier `data/referentiel/` sous le préfixe `referentiel/`, puis liste le contenu du bucket pour confirmation.
10. Exécution du script et vérification visuelle dans la console MinIO (`http://localhost:9001`) que les 4 fichiers sont bien présents sous `anfa-raw/referentiel/`.
11. Capture d'écran de la console MinIO, déposée dans `captures/bucket-anfa-raw.png`.
12. Rédaction de ce `RENDU.md`, ajout du dossier `seance-01/` au dépôt, commit et push de la branche `seance-01` vers le fork distant.

## Capture d'écran

La capture montre le bucket `anfa-raw`, avec le préfixe `referentiel/` contenant les 4 fichiers
`arrets.csv`, `bus.csv`, `lignes.csv` et `tarifs.csv`.

## Difficultés rencontrées

- **Python non reconnu sous Windows** : quand j'ai tapé `python3 -m venv .venv`, j'ai eu le  message *"Python was not found; run without arguments to install from the Microsoft Store..."*. Windows me redirigeait vers un faux alias du Microsoft Store au lieu de trouver mon installation réelle de Python. J'ai résolu ça en utilisant la commande `py` (le lanceur Python officiel sous Windows) à la place de `python3` : `py -m venv .venv`.

- **Mauvais chemin d'activation de l'environnement virtuel** : la commande du TP,`source .venv/bin/activate`, m'a renvoyé l'erreur *"No such file or directory"*. En cherchant,
 j'ai compris que sous Windows (même dans Git Bash), le dossier généré par `venv` s'appelle `Scripts/` et non `bin/`. J'ai corrigé avec la bonne commande : `source .venv/Scripts/activate`.

- **Script Python mal indenté après copier-coller** : en copiant le script `upload_referentiel.py` depuis le support de cours, j'ai perdu toute l'indentation des blocs
  (fonctions, `try/except`, boucles). Or en Python, l'indentation est obligatoire pour que le code soit valide. J'ai résolu ça en faisait une indentation cohérente  du fichier 

- **Erreur YAML dans `docker-compose.yml`** : `docker compose up -d` m'a renvoyé l'erreur *"mapping key 'volumes' already defined"*. La cause était la même que pour le script Python : j'avais perdu l'indentation du fichier YAML , ce qui faisait que mes deux blocs `volumes:` (celui du service `minio` et celui de la déclaration globale du volume) se
retrouvaient au même niveau, créant un conflit de clé. J'ai résolu ça en réécrivant le fichier avec l'indentation correcte  et en validant la syntaxe avec 
`docker compose config` avant de relancer.


## Exercices d'application

### Exercice 1 : QCM conceptuel

**1.1** Réponse : **D** — Open source obligatoire.
Justification : Selon la définition du NIST (National Institute of Standards and Technology), les cinq caractéristiques essentielles du cloud computing sont le libre-service à la demande, l'accès réseau étendu, la mutualisation des ressources, l'élasticité rapide et le service mesuré ; l'utilisation de logiciels open source n'est pas une exigence du cloud computing.

**1.2** Réponse : **C** — SaaS.
Justification : Gmail est une application complète accessible via Internet, sans que l'utilisateur ait à gérer l'infrastructure ou la plateforme sous-jacente ; il s'agit donc d'un service de type Software as a Service (SaaS).

**1.3** Réponse : **D** — FaaS.
Justification : Le besoin décrit (déclenchement à l'arrivée d'un évènement, exécution en quelques millisecondes, absence de serveur permanent) correspond exactement au modèle Function as a Service : on ne paie et ne provisionne que le temps d'exécution de la fonction, sans gérer de serveur sous-jacent.

**1.4** Réponse : **C** — Cloud hybride.
Justification : Le cloud hybride permet de garder les données sensibles soumises à régulation dans un environnement privé/contrôlé, tout en exploitant l'élasticité du cloud public pour les traitements non sensibles. C'est la seule option qui répond aux deux contraintes simultanément.

**1.5** Réponse : **B** — La situation où une entreprise ne peut plus changer de fournisseur sans coûts ou risques majeurs.
Justification : Le vendor lock-in désigne la dépendance technique ou contractuelle qui rend la migration vers un autre fournisseur coûteuse ou risquée (formats propriétaires, API non standard, coûts de sortie des données, etc.), pas un acte juridique ou une technique de chiffrement.

**1.6** Réponse : **C** — Un service open source est forcément moins performant qu'un service managé propriétaire.
Justification : C'est faux : la performance dépend de l'implémentation, de l'architecture et du contexte d'utilisation, pas du modèle de licence. De nombreux outils open source (Kafka, Spark, MinIO) sont utilisés en production à très grande échelle, y compris par les fournisseurs cloud eux-mêmes pour leurs propres services managés.

### Exercice 2 : Classification de services

| Service                   | Modèle | Justification                                                                   |
| ------------------------- | ------ | ------------------------------------------------------------------------------- |
| Google Compute Engine     | IaaS   | Fournit des machines virtuelles que l'utilisateur administre.                   |
| AWS Lambda                | FaaS   | Exécute du code à la demande sans gérer de serveur.                             |
| Snowflake                 | SaaS   | Entrepôt de données entièrement géré et accessible comme service.               |
| Heroku                    | PaaS   | Plateforme permettant de déployer des applications sans gérer l'infrastructure. |
| Microsoft 365             | SaaS   | Applications bureautiques accessibles via Internet.                             |
| Databricks                | PaaS   | Plateforme managée pour l'exécution de traitements Big Data et IA.              |
| Microsoft Azure Functions | FaaS   | Exécution de fonctions déclenchées par événements.                              |
| Tableau Online            | SaaS   | Solution de visualisation et de tableaux de bord accessible via le web.         |



### Exercice 3 : Lecture et interprétation

**3.1 Commande `docker run`**

docker run -d --name analyse-anfa -p 8888:8888 -v /home/koffi/notebooks:/notebooks \
-e JUPYTER_TOKEN=anfa-token \
jupyter/pyspark-notebook

-d : Exécute le conteneur en arrière-plan (mode détaché).

--name analyse-anfa : Attribue le nom analyse-anfa au conteneur.

-p 8888:8888 : Expose le port 8888 du conteneur sur le port 8888 de l'hôte.

-v /home/koffi/notebooks:/notebooks : Monte le dossier local /home/koffi/notebooks dans le répertoire /notebooks du conteneur.

-e JUPYTER_TOKEN=anfa-token : Définit la variable d'environnement JUPYTER_TOKEN pour sécuriser l'accès à Jupyter.

jupyter/pyspark-notebook : Image Docker utilisée pour créer le conteneur.

En résumé cette commande lance un conteneur Jupyter Notebook avec PySpark préinstallé en arrière-plan. Les notebooks sont stockés sur le disque local et l'accès à l'interface web est disponible sur http://localhost:8888 avec le token anfa-token.

**3.2 Lecture d'un `docker-compose.yml`**

a. **Adresses accessibles depuis le navigateur de l'hôte :**
`http://localhost:9000` (API S3, utilisée par les programmes) et `http://localhost:9001`
(console web d'administration), grâce au mapping des ports `9000:9000` et `9001:9001`.

b. **Suppression du conteneur puis relance avec `docker compose up -d` :**
Les données ne sont **pas perdues**. Le conteneur lui-même est éphémère (il ne stocke rien de durable dans son propre système de fichiers), mais les données sont écrites dans le volume nommé `minio-data`, qui est une entité Docker indépendante du cycle de vie du conteneur. Supprimer le conteneur avec `docker rm` ne supprime pas le volume associé ; quand `docker compose up -d` recrée un nouveau conteneur, celui-ci remonte automatiquement le même volume `minio-data` et retrouve donc toutes les données précédemment écrites.

c. **Problème de sécurité à corriger en production :**
Les identifiants `MINIO_ROOT_USER` et `MINIO_ROOT_PASSWORD` sont écrits **en clair** dans le fichier YAML. Si ce fichier est versionné dans un dépôt Git (même privé), le mot de passe root se retrouve exposé dans l'historique. En production, ces secrets devraient être injectés via un gestionnaire de secrets dédié (Docker secrets, Vault, AWS Secrets Manager, variables d'environnement non versionnées, etc.) plutôt que codés en dur dans un fichier de configuration.

### Exercice 4 : Diagnostic

**a. Cause précise de l'erreur :**
Le script utilise les identifiants `anfa-admin` / `anfa-password-2026`, qui sont les identifiants **root** du serveur MinIO (définis via `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`), et non la clé applicative `anfa-app-key` / `anfa-app-secret-2026` créée spécifiquement pour l'API S3 via `mc admin user svcacct add`. L'API S3 de MinIO ne reconnaît pas `anfa-admin` comme une "Access Key Id" valide dans son système de clés applicatives, d'où l'erreur `InvalidAccessKeyId`.

**b. Correction du code :**
Remplacer les valeurs d'identifiants par celles de la clé applicative créée en partie 3.4 :

```python
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="anfa-app-key",
    aws_secret_access_key="anfa-app-secret-2026",
    region_name="us-east-1",
)
```

**c. Pourquoi `anfa-admin` fonctionne sur la console web mais pas sur l'API S3 :**
La console web d'administration et l'API S3 ne valident pas les identifiants de la même façon.Le compte root (`anfa-admin`) est conçu pour l'administration globale du serveur (configuration, gestion des utilisateurs, des politiques, etc.), accessible via la console web ou l'API d'administration de MinIO. L'API S3 (utilisée par `boto3`/`s3.upload_file`), elle, attend des identifiants de type "Access Key / Secret Key" associés à un compte de service (`svcacct`), créés
explicitement pour cet usage. Le compte root n'est délibérément pas exposé de la même manière sur l'API S3 — c'est une mesure de sécurité qui empêche d'utiliser le mot de passe root le plus puissant du système directement comme credentials applicatifs dans du code, limitant ainsi les conséquences d'une fuite de ces credentials.

### Exercice 5 : Mini-cas d'architecture

**a. Deux limites concrètes de l'architecture actuelle :**
1. **Absence de temps réel** : un export CSV mensuel ne permet en aucun cas des prédictions "quasi temps réel" à l'heure ; les données sont par construction obsolètes de plusieurs semaines au moment de l'analyse.
2. **Absence de partage et de scalabilité** : le modèle tourne sur l'ordinateur portable d'une seule personne (Toyi). Aucun autre analyste ne peut y accéder, et la capacité de calcul est strictement limitée à celle de cette machine — impossible d'absorber un pic de charge le vendredi soir ou pendant les fêtes.

**b. Besoins de la direction et caractéristiques NIST correspondantes :**

| Besoin                              | Caractéristique NIST                         | Explication                                                                        |
| ----------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------- |
| Prédictions chaque heure            | Élasticité rapide                            | Les ressources peuvent être allouées automatiquement selon la charge.              |
| Tableau de bord partagé             | Accès réseau étendu                          | Les utilisateurs accèdent au service via Internet depuis différents appareils.     |
| Augmenter la capacité lors des pics | Élasticité rapide                            | Les ressources augmentent ou diminuent automatiquement.                            |
| Maîtriser les coûts                 | Service mesuré                               | Paiement selon l'usage réel des ressources.                                        |
| Données sous contrôle               | Mutualisation contrôlée / déploiement adapté | Les données peuvent rester dans un environnement privé tout en profitant du cloud. |


**c. Modèle de service par composant :**

(i) **Tableau de bord partagé** → **SaaS** : les analystes doivent y accéder sans aucune installation locale ; un outil de visualisation prêt à l'emploi (type Tableau Online ou équivalent) correspond exactement à ce besoin.

(ii) **Calcul des prédictions à l'heure** → **FaaS** : un traitement déclenché à intervalle régulier (chaque heure), de durée limitée, sans besoin de serveur tournant en permanence, est le cas d'usage typique du Function as a Service.

(iii) **Stockage des données clients** → **IaaS** (ou stockage géré bas niveau type S3 compatible) : la sensibilité réglementaire de ces données exige un contrôle fin sur leur localisation, leur chiffrement et leur accès, ce qu'un modèle plus bas niveau (infrastructure de stockage maîtrisée) permet mieux qu'un SaaS totalement opaque.

**d. Modèle de déploiement recommandé :** Un **cloud hybride** est recommandé. Il permet de conserver les données clients sensibles dans un environnement privé/contrôlé pour respecter les contraintes de conformité, tout en exploitant l'élasticité et la flexibilité du cloud public pour les traitements non sensibles (calcul des prédictions, tableau de bord). Cette approche concilie les deux exigences apparemment contradictoires de la direction : conformité stricte et élasticité.

**e. Trois stratégies pour limiter le vendor lock-in :**
1. **Utiliser des outils open source et standards** (ex. MinIO compatible S3, Kafka, PostgreSQL) plutôt que des services propriétaires fortement intégrés à un fournisseur spécifique.
2. **Conteneuriser les applications** (Docker/Kubernetes) afin de pouvoir redéployer les mêmes charges de travail chez un autre fournisseur cloud sans réécriture majeure.
3. **Éviter les API et formats propriétaires non standard** (privilégier des interfaces ouvertes comme l'API S3, des formats de données ouverts comme Parquet/CSV) pour garder la possibilité demigrer les données et le code vers un autre prestataire avec un effort limité.
