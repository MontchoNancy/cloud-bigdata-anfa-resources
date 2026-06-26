
# Rendu Séance 3

**Nom et prénom :** Nancy Montcho
**Identifiant GitHub :** MontchoNancy

## Résumé de la séance

Cette troisième séance introduit Kubernetes comme orchestrateur de conteneurs à grande échelle. Après avoir utilisé Docker Compose pour orchestrer quelques services sur une seule machine, j'ai découvert comment Kubernetes permet de gérer des conteneurs sur un cluster de plusieurs nœuds, avec des mécanismes automatiques de résilience, de scaling et de mise à jour. J'ai déployé MinIO dans un cluster Kind local en écrivant des manifestes YAML (PersistentVolumeClaim, Deployment, Service), utilisé `kubectl` pour interagir avec le cluster, et accédé à la console MinIO via `kubectl port-forward`. La séance illustre concrètement la différence entre Docker Compose (outil de développement local) et Kubernetes (orchestrateur de production).

## Étapes principales

1. Installation de `kind` via `winget` et création du cluster Kubernetes local `anfa` avec `kind create cluster --name anfa`.
2. Vérification du cluster avec `kubectl cluster-info` et `kubectl get nodes`.
3. Installation du contrôleur Ingress NGINX dans le cluster avec `kubectl apply`.
4. Écriture du manifeste `minio-pvc.yaml` : PersistentVolumeClaim de 2 Gi pour la persistance des données MinIO.
5. Écriture du manifeste `minio-deployment.yaml` : Deployment MinIO avec variables d'environnement et montage du PVC.
6. Écriture du manifeste `minio-service.yaml` : Service de type NodePort exposant les ports 9000 et 9001.
7. Application des manifestes avec `kubectl apply -f` et vérification avec `kubectl get pods`, `kubectl get pvc`, `kubectl get svc`.
8. Accès à la console MinIO via `kubectl port-forward service/minio 9001:9001` et capture d'écran.
9. Rédaction de ce `RENDU.md` et push sur la branche `seance-03`.

## Difficultés rencontrées

- **`kind` non reconnu après installation** : winget modifie le PATH mais PowerShell ne recharge pas automatiquement les variables d'environnement. Résolu en forçant le rechargement avec `$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")`.

- **Commandes multi-lignes avec `\` dans PowerShell** : le `\` est un caractère de continuation sous Linux/Git Bash mais pas sous PowerShell. Résolu en mettant les commandes longues sur une seule ligne.

- **Cluster inaccessible après redémarrage du PC** : Docker Desktop ne redémarre pas automatiquement, ce qui rend le cluster Kind inaccessible. Résolu en relançant Docker Desktop manuellement puis en reconnectant kubectl avec `kubectl cluster-info --context kind-anfa`.

- **`port-forward` refusé** : le port-forward échouait car Docker Desktop n'était pas démarré. Résolu après redémarrage de Docker Desktop et relance du cluster.

## Capture d'écran

La capture montre la console MinIO accessible via `kubectl port-forward`, avec le bucket `anfa-raw` contenant le dossier `referentiel/` et ses 4 fichiers CSV (11.1 KiB — données persistées depuis la séance 2).

## Exercices d'application

### Exercice 1 : QCM conceptuel

**1.1** Réponse : **B** — Kubernetes orchestre des conteneurs sur un cluster de machines, en s'appuyant sur un container runtime.
Justification : Kubernetes ne remplace pas Docker mais s'appuie sur un container runtime (containerd, CRI-O) pour gérer le cycle de vie des conteneurs sur un ensemble de machines.

**1.2** Réponse : **B** — etcd.
Justification : etcd est le magasin clé-valeur distribué du Control Plane qui stocke l'intégralité de l'état du cluster (configurations, ressources, secrets).

**1.3** Réponse : **C** — Scheduler.
Justification : Le Scheduler est le composant du Control Plane qui analyse les ressources disponibles sur chaque nœud et décide sur lequel un nouveau pod doit être placé.

**1.4** Réponse : **C** — À l'API Server, qui est le point d'entrée unique du cluster.
Justification : Toute commande `kubectl` passe par l'API Server, qui est le seul composant du Control Plane exposé à l'extérieur ; il authentifie, valide et route ensuite la requête.

**1.5** Réponse : **B** — Le Deployment recrée immédiatement un nouveau pod pour respecter l'état souhaité.
Justification : Un Deployment définit un état souhaité (ex. 2 replicas) ; le Controller Manager détecte l'écart et ordonne la création d'un nouveau pod pour y revenir.

**1.6** Réponse : **B** — NodePort.
Justification : Un Service de type NodePort expose un port statique sur chaque nœud du cluster, permettant l'accès depuis l'extérieur sans nécessiter un load balancer cloud.

**1.7** Réponse : **B** — Elle modifie l'état souhaité du Deployment à 5 replicas ; Kubernetes converge vers ce nombre.
Justification : Kubernetes fonctionne par réconciliation : la commande met à jour l'état désiré dans etcd, et le Controller Manager crée ou supprime des pods pour atteindre ce nombre.

**1.8** Réponse : **B** — À isoler logiquement les ressources (séparation par équipe, environnement, ou application).
Justification : Les Namespaces permettent de partitionner un cluster en environnements distincts (dev, staging, prod) ou par équipe, sans isolation réseau stricte mais avec des politiques de contrôle d'accès.

**1.9** Réponse : **B** — Des conteneurs Docker.
Justification : Kind (Kubernetes IN Docker) simule les nœuds d'un cluster Kubernetes en les faisant tourner comme des conteneurs Docker sur la machine hôte, ce qui le rend léger et idéal pour le développement local.

---

### Exercice 2 : Lecture et interprétation d'un manifeste

**2.1 Rôle de `selector.matchLabels` et lien avec `template.metadata.labels`**

`selector.matchLabels` indique au Deployment quels pods il doit gérer : il sélectionne tous les pods dont les labels correspondent à `app: anfa-api`. `template.metadata.labels` définit les labels appliqués à chaque pod créé par ce Deployment. Ces deux champs doivent être identiques : si les labels du template ne correspondent pas au selector, Kubernetes refuse le manifeste car le Deployment ne pourrait pas reconnaître ses propres pods.

**2.2 Nombre de pods et comportement en cas de mort**

Ce Deployment crée **2 pods** (champ `replicas: 2`). Si l'un d'eux meurt (crash, nœud défaillant), le Controller Manager détecte immédiatement l'écart entre l'état réel (1 pod) et l'état souhaité (2 pods), et ordonne la création d'un nouveau pod pour revenir à 2.

**2.3 Pourquoi `minio` et pas une adresse IP**

`minio` est le nom du Service Kubernetes qui expose le Deployment MinIO. Kubernetes intègre un DNS interne (CoreDNS) qui résout automatiquement les noms de services en adresses IP de cluster. Utiliser le nom de service plutôt qu'une IP est indispensable car les adresses IP des pods changent à chaque redémarrage, tandis que le nom du service reste stable.

**2.4 Conséquence de l'absence de Service**

Sans Service, les pods `anfa-api` sont inaccessibles depuis l'extérieur du cluster et même depuis les autres pods (sauf en connaissant l'IP éphémère du pod). Concrètement, aucune application mobile ne pourrait appeler l'API, et MinIO ne pourrait pas non plus y accéder via un nom stable.

**2.5 Manifeste de Service ClusterIP**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: anfa-api
  namespace: anfa
spec:
  type: ClusterIP
  selector:
    app: anfa-api
  ports:
    - port: 80
      targetPort: 8000
```

---

### Exercice 3 : Diagnostic

**3.1 Le pod qui ne démarre pas**

a. **Signification de `ImagePullBackOff`** : Kubernetes n'a pas réussi à télécharger l'image Docker spécifiée depuis le registre. Il réessaie à intervalles croissants (backoff exponentiel) d'où le terme "BackOff".

b. **Cause probable** : le nom de l'image contient une faute de frappe — `minio/miniooo:latest` n'existe pas sur Docker Hub. L'image correcte est `minio/minio:latest`.

c. **Commande pour plus de détails** :
```bash
kubectl describe pod minio-7d9f8b6c5-x2k9p
```
La section `Events` en bas de la sortie indique précisément l'erreur (ex. `Failed to pull image "minio/miniooo:latest": ... not found`).

---

**3.2 Le PVC qui ne se lie pas**

a. **Signification de `Pending`** : le PVC n'a pas encore trouvé de PersistentVolume disponible qui corresponde à ses critères (taille, mode d'accès, StorageClass). Il attend qu'un volume soit provisionné.

b. **Cause probable dans Kind** : le PVC demande **500 Gi** de stockage. Dans un cluster Kind local, le provisioner par défaut (`standard`) est limité par l'espace disque réel de la machine hôte. Une demande de 500 Gi dépasse très probablement la capacité disponible, laissant le PVC en `Pending` indéfiniment.

c. **Commande de diagnostic** :
```bash
kubectl describe pvc data-pvc
```
La section `Events` indiquera si le provisioner a échoué et pourquoi.

---

**3.3 Le port-forward qui échoue**

a. **Cause de l'erreur** : `kubectl port-forward` nécessite que le pod ciblé soit dans l'état `Running`. Ici le pod est en `Pending` (pas encore schedulé ou en attente de ressources), donc il n'y a pas de processus auquel se connecter.

b. **Commande pour comprendre le Pending** :
```bash
kubectl describe pod <nom-du-pod>
```
ou
```bash
kubectl get events --sort-by=.lastTimestamp
```

c. **Ordre logique à respecter** :
1. Appliquer les manifestes (`kubectl apply -f`)
2. Attendre que le pod soit `Running` (`kubectl get pods`)
3. Vérifier que le Service existe (`kubectl get svc`)
4. Lancer le `port-forward` seulement quand le pod est `Running`

---

### Exercice 4 : De Docker Compose à Kubernetes

**4.1 Manifestes Kubernetes nécessaires**

Pour reproduire le service MinIO de Docker Compose, il faut **3 manifestes distincts** :

| Manifeste | Kind | Rôle |
|---|---|---|
| `minio-pvc.yaml` | PersistentVolumeClaim | Demande de stockage persistant (équivalent du volume nommé `minio-data`) |
| `minio-deployment.yaml` | Deployment | Déploie le conteneur MinIO avec ses variables d'environnement et monte le PVC |
| `minio-service.yaml` | Service | Expose MinIO sur le réseau du cluster et vers l'extérieur (NodePort) |

**4.2 Volume Docker nommé vs PersistentVolumeClaim**

En Docker Compose, un volume nommé (`minio-data`) est un répertoire géré par Docker sur la machine hôte — simple, local, et lié à cette machine. En Kubernetes, un PersistentVolumeClaim est une **demande abstraite de stockage** : le cluster cherche (ou provisionne dynamiquement) un PersistentVolume qui satisfait les critères (taille, mode d'accès, StorageClass), indépendamment du nœud sur lequel tourne le pod. Cette abstraction permet au stockage de survivre aux redémarrages de pods sur n'importe quel nœud du cluster.

**4.3 Pourquoi port-forward avec Kind et pas avec Compose**

Avec Docker Compose, `-p 9001:9001` mappe directement le port du conteneur sur un port de la machine hôte — c'est une fonctionnalité native de Docker sur une seule machine. Avec Kubernetes et Kind, les nœuds sont eux-mêmes des conteneurs Docker ; un Service NodePort expose le port sur le nœud Kind, mais ce nœud n'est pas directement accessible depuis l'hôte. `kubectl port-forward` crée un tunnel entre la machine locale et le pod via l'API Server. Pour un accès direct sans port-forward, il faudrait configurer Kind avec `extraPortMappings` dans sa configuration pour mapper les ports des nœuds vers l'hôte.

**4.4 Deux apports de Kubernetes observés en TP**

1. **Résilience automatique** : Kubernetes surveille en permanence l'état des pods et les recrée automatiquement en cas de défaillance, sans intervention manuelle — ce que Docker Compose ne fait pas nativement.

2. **Abstraction du stockage avec le PVC** : le PersistentVolumeClaim dissocie la demande de stockage de son implémentation physique, permettant à MinIO de retrouver ses données même si le pod est recréé sur un nœud différent.

---

### Exercice 5 : Mini-cas d'architecture

**5.1 Type d'objet Kubernetes par composant**

| Composant | Objet Kubernetes | Justification |
|---|---|---|
| `pipeline-anfa` | **CronJob** | Le pipeline tourne chaque nuit à 2h du matin selon un planning fixe ; CronJob est conçu exactement pour les tâches périodiques planifiées. |
| `anfa-api` | **Deployment** | L'API REST doit être continuellement disponible avec plusieurs replicas ; le Deployment gère le cycle de vie, le rolling update et le scaling horizontal. |
| `anfa-dashboard` | **Deployment** | Grafana est une application stateless (les données sont dans une base externe) qui doit rester disponible en journée ; un Deployment simple suffit. |

**5.2 Paramètres HPA pour `anfa-api`**

```yaml
minReplicas: 2
maxReplicas: 10
metric: CPU — targetAverageUtilization: 60
```

Avec ~50 req/s aux heures de pointe et ~5 req/s le reste du temps, un minimum de 2 replicas garantit la disponibilité en cas de défaillance d'un pod. Le maximum de 10 couvre les pics de charge sans sur-provisionner en permanence. Une cible CPU à 60% laisse de la marge pour absorber les pics avant que l'autoscaler ait le temps de réagir.

**5.3 Type de Service pour `anfa-api`**

**LoadBalancer** — L'API REST est consommée par des applications mobiles externes au cluster, dans un environnement cloud managé. Le type LoadBalancer provisionne automatiquement un load balancer cloud avec une IP publique stable, distribue le trafic entre les replicas et est la solution standard en production cloud pour exposer des services publics.

**5.4 Gestion des mises à jour sans coupure**

Kubernetes utilise par défaut une stratégie de **Rolling Update** : il recrée les pods progressivement, en remplaçant les anciens par les nouveaux un par un (ou par groupe). À tout moment, un minimum de pods restent disponibles pour traiter les requêtes. Concrètement, Kubernetes démarre un nouveau pod avec la nouvelle image, attend qu'il soit `Ready` (healthcheck OK), puis termine un ancien pod — et ainsi de suite jusqu'à remplacement complet. Cela garantit qu'il n'y a jamais de coupure visible pour les utilisateurs.

**5.5 Manifeste Deployment pour `anfa-api`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anfa-api
  namespace: anfa
spec:
  replicas: 3
  selector:
    matchLabels:
      app: anfa-api
  template:
    metadata:
      labels:
        app: anfa-api
    spec:
      containers:
        - name: api
          image: anfa/api:v1
          ports:
            - containerPort: 8000
          env:
            - name: MINIO_ENDPOINT
              value: "http://minio:9000"
```
