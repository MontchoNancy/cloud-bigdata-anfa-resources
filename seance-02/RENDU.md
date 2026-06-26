# Rendu Séance 2

**Nom et prénom :** Nancy Montcho
**Identifiant GitHub :** MontchoNancy

## Exercices d'application

### Exercice 1 : QCM conceptuel

**1.1** Réponse : **C** — Un conteneur partage le noyau de la machine hôte.
Justification : Un conteneur n'embarque pas son propre noyau Linux ; il partage celui de la machine hôte via les namespaces et cgroups, ce qui le rend beaucoup plus léger qu'une machine virtuelle.

**1.2** Réponse : **B** — L'image est un modèle figé en lecture seule ; le conteneur est une instance en cours d'exécution.
Justification : L'image est un artefact statique (comme un template), tandis que le conteneur est l'instance vivante et active issue de cette image.

**1.3** Réponse : **B** — Les namespaces.
Justification : Docker utilise les namespaces du noyau Linux pour isoler chaque conteneur : réseau, processus, système de fichiers et utilisateurs sont vus de façon indépendante par chaque conteneur.

**1.4** Réponse : **A** — Les cgroups.
Justification : Les cgroups (control groups) permettent à Docker de limiter et contrôler les ressources consommées par un conteneur, notamment le CPU, la mémoire et les I/O disque.

**1.5** Réponse : **B** — Dans une machine virtuelle Linux invisible gérée par Docker Desktop.
Justification : Sous macOS, le noyau ne supporte pas nativement les namespaces et cgroups Linux ; Docker Desktop démarre donc une VM Linux légère en arrière-plan pour faire tourner les conteneurs.

**1.6** Réponse : **B** — La société d'origine qui a créé et open-sourcé Docker en 2013.
Justification : DotCloud était une PaaS cloud qui a développé Docker en interne avant de l'ouvrir à la communauté en 2013, puis de se renommer Docker Inc.

**1.7** Réponse : **C** — Docker a apporté un format d'image portable, une CLI simple et un registre public.
Justification : Docker n'a pas inventé les namespaces ni les cgroups (déjà présents dans LXC), mais il a standardisé la distribution des images via Docker Hub et simplifié leur usage avec une CLI intuitive.

**1.8** Réponse : **B** — Open Container Initiative — une norme ouverte pour les images et le runtime.
Justification : L'OCI est une organisation fondée en 2015 qui définit des standards ouverts pour garantir l'interopérabilité entre les différents outils de conteneurisation (Docker, Podman, containerd, etc.).

---

### Exercice 2 : Lecture et analyse d'un Dockerfile

Le Dockerfile analysé :

```dockerfile
FROM python:3.11
WORKDIR /application
COPY . /application
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "main.py"]
```

**2.1 Explication de chaque instruction**

| Instruction | Explication |
|---|---|
| `FROM python:3.11` | Définit l'image de base : Python 3.11 sur Debian. C'est le point de départ de l'image. |
| `WORKDIR /application` | Crée et définit le répertoire de travail courant à `/application` pour les instructions suivantes. |
| `COPY . /application` | Copie tous les fichiers du contexte de build local dans le répertoire `/application` du conteneur. |
| `RUN pip install -r requirements.txt` | Exécute l'installation des dépendances Python listées dans `requirements.txt` au moment du build. |
| `EXPOSE 5000` | Déclare que le conteneur écoute sur le port 5000 (documentation uniquement, n'ouvre pas le port). |
| `CMD ["python", "main.py"]` | Définit la commande par défaut exécutée au démarrage du conteneur. |

**2.2 Différence entre EXPOSE et -p**

`EXPOSE 5000` est une déclaration documentaire dans le Dockerfile : elle informe les développeurs et les outils que le conteneur utilise ce port, mais n'ouvre rien réellement. `-p 5000:5000` dans `docker run` publie effectivement le port en mappant le port 5000 du conteneur sur le port 5000 de la machine hôte. En résumé : `EXPOSE` documente, `-p` ouvre vraiment.

**2.3 Deux problèmes selon les bonnes pratiques**

*Problème 1 : Image de base trop lourde.* `python:3.11` est une image complète basée sur Debian (~900 Mo) qui inclut de nombreux outils inutiles en production. Correction : utiliser `python:3.11-slim-bookworm` (~150 Mo).

*Problème 2 : Mauvais ordre des instructions (cache non optimisé).* `COPY . /application` est placé avant `RUN pip install`, donc chaque modification du code source invalide le cache et force une réinstallation complète des dépendances. Correction : copier d'abord uniquement `requirements.txt`, installer les dépendances, puis copier le reste du code.

**2.4 Version corrigée du Dockerfile**

```dockerfile
FROM python:3.11-slim-bookworm

WORKDIR /application

# Optimisation du cache : requirements avant le code source
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Utilisateur non-root pour la sécurité
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 5000

CMD ["python", "main.py"]
```

---

### Exercice 3 : Diagnostic

**3.1 Le build qui échoue**

a. **Cause précise de l'erreur :** Le `RUN pip install -r requirements.txt` est exécuté avant le `COPY . .`. Au moment où pip cherche le fichier, il n'existe pas encore dans le système de fichiers du conteneur.

b. **Correction du Dockerfile :**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

c. **Mauvaise compréhension illustrée :** Cette erreur montre que l'étudiant a confondu le système de fichiers de sa machine hôte et celui du conteneur. Dans Docker, les fichiers locaux n'existent dans le conteneur qu'après une instruction `COPY` ou `ADD` ; chaque instruction `RUN` s'exécute dans l'état du système de fichiers tel qu'il est à ce moment précis du build.

**3.2 Le conteneur qui ne voit pas l'autre**

a. **Erreur dans le DATABASE_URL :** L'URL utilise `localhost`, qui à l'intérieur du conteneur `api` désigne le conteneur `api` lui-même, pas le conteneur `db`.

b. **Correction :** Remplacer `localhost` par le nom du service Docker Compose :

```
DATABASE_URL: "postgresql://user:password@db:5432/anfa"
```

Docker Compose crée automatiquement un réseau interne et résout les noms de services comme des noms DNS.

---

### Exercice 4 : Optimisation d'image

Le Dockerfile analysé :

```dockerfile
FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y curl wget git build-essential
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
CMD ["python3", "downloader.py"]
```

**a. Quatre problèmes identifiés**

| # | Problème | Explication |
|---|---|---|
| 1 | **Image de base trop lourde** | `ubuntu:22.04` nécessite une installation manuelle de Python. `python:3.11-slim` inclut déjà Python et est bien plus légère. |
| 2 | **Outils inutiles installés** | `curl`, `wget`, `git`, `build-essential` ne sont pas nécessaires pour `requests==2.31.0`. Ils gonflent l'image et augmentent la surface d'attaque. |
| 3 | **Couches RUN fragmentées** | Chaque `RUN apt-get` crée une couche séparée avec le cache apt non nettoyé, augmentant inutilement la taille finale de l'image. |
| 4 | **Pas d'utilisateur non-root** | Le conteneur tourne en `root` : une faille dans l'application donnerait un accès root complet au conteneur. |

**b. Version optimisée**

```dockerfile
# Image Python légère : Python inclus, taille réduite (~150 Mo vs ~900 Mo)
FROM python:3.11-slim-bookworm

WORKDIR /app

# requirements.txt en premier pour optimiser le cache Docker
COPY requirements.txt .

# Installation sans cache pip pour réduire la taille de l'image
RUN pip install --no-cache-dir -r requirements.txt

# Code source copié après les dépendances
COPY . .

# Utilisateur non-root pour éviter les élévations de privilèges
RUN adduser --disabled-password --gecos "" appuser
USER appuser

CMD ["python", "downloader.py"]
```

---

### Exercice 5 : Mini-cas d'architecture

**a. Services à conteneuriser**

| Service | Rôle |
|---|---|
| `ftp-fetcher` | Script Python qui se connecte au FTP toutes les nuits, télécharge le fichier JSON Lines, le nettoie et écrit les résultats agrégés dans MinIO. |
| `minio` | Stockage objet S3-compatible qui conserve les fichiers bruts et les résultats agrégés du pipeline. |
| `jupyter` | Environnement de notebooks pour que l'équipe data explore les données stockées dans MinIO et crée des graphiques. |

**b. Restart policy pour le script FTP**

Recommandation : **`on-failure`**. Le script FTP est une tâche ponctuelle (batch nocturne) : il doit démarrer, s'exécuter, puis s'arrêter avec le code 0. La policy `on-failure` relance le conteneur uniquement en cas d'erreur (code de sortie non nul), sans le relancer indéfiniment après une exécution réussie. Les policies `always` et `unless-stopped` le relanceraient en boucle même après un succès, ce qui n'est pas souhaitable pour un batch.

**c. Passer la date au script**

*Mécanisme 1 : Variable d'environnement* — le script lit `os.environ["TARGET_DATE"]` sans modification du code :

```yaml
ftp-fetcher:
  environment:
    TARGET_DATE: "2026-06-23"
```

*Mécanisme 2 : Argument de commande via `command:`* :

```yaml
ftp-fetcher:
  command: ["python", "fetcher.py", "--date", "2026-06-23"]
```

**Recommandation : la variable d'environnement** — plus flexible pour l'automatisation (cron, orchestrateur), sans modifier le `docker-compose.yml` ni le code Python.

**d. Pourquoi ne pas mettre le script dans Jupyter ?**

Mettre le script de pipeline dans le conteneur Jupyter violerait le principe de responsabilité unique : Jupyter est un outil d'exploration interactive, pas un exécuteur de batch. Mélanger les deux rend la maintenance difficile (on ne peut pas redémarrer ou scaler le pipeline sans impacter les notebooks), complique les droits d'accès et rend les logs illisibles. De plus, si Jupyter est arrêté pour économiser des ressources, le pipeline s'arrêterait aussi. Séparer les services garantit leur indépendance, leur clarté et leur robustesse.

**e. Squelette de docker-compose.yml**

```yaml
services:

  minio:
    image: minio/minio:latest
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: anfa-admin
      MINIO_ROOT_PASSWORD: anfa-password-2026
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - minio-data:/data
    ports:
      - "9000:9000"
      - "9001:9001"

  ftp-fetcher:
    build:
      context: ./ftp-fetcher
      dockerfile: Dockerfile
    restart: on-failure
    environment:
      TARGET_DATE: "2026-06-23"
      MINIO_ENDPOINT: "http://minio:9000"
    depends_on:
      minio:
        condition: service_healthy
    volumes:
      - ./data:/data

  jupyter:
    image: jupyter/scipy-notebook:latest
    restart: unless-stopped
    environment:
      JUPYTER_TOKEN: anfa-token
    depends_on:
      minio:
        condition: service_healthy
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jovyan/work

volumes:
  minio-data:
```
