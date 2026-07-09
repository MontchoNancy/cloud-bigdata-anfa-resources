# RENDU — Séance 6 : Orchestration du pipeline Anfa avec Apache Airflow

**Nom :** MONTCHO Nancy
**Master 1 IA/Big Data — ESGIS**
**Cours :** Cloud & Big Data — Denis AKPAGNONITE

---

## Résumé

Cette séance a consisté à déployer une stack complète Airflow + MinIO + Spark via Docker Compose, puis à écrire et exécuter deux DAGs : un DAG d'initiation (`hello_anfa`, 2 tâches) et un DAG métier complet (`anfa_pipeline_quotidien`, 4 tâches) qui automatise le pipeline construit à la main en séance 5 : génération de trajets simulés, analyse Spark des heures de pointe, vérification des résultats dans MinIO, et notification.

J'ai également observé, en cassant volontairement une tâche, comment Airflow gère les échecs : retries automatiques, passage en `failed`, propagation en `upstream_failed` pour les tâches suivantes, puis reprise du pipeline exactement là où il s'était arrêté après correction — sans tout rejouer depuis le début.

## Étapes principales

1. Synchronisation du fork avec le dépôt du cours (`upstream`) et création de la branche `seance-06`.
2. Lancement de la stack Docker Compose (Postgres, Airflow scheduler/webserver, MinIO, Spark master/worker).
3. Préparation de MinIO : création des buckets `anfa-raw` et `anfa-processed`, et de la clé applicative `anfa-app-key`.
4. Connexion à l'UI Airflow (`localhost:8088`) et découverte du DAG `hello_anfa` (2 tâches, déclenchement manuel, dépendance simple `t1 >> t2`).
5. Exécution du DAG métier `anfa_pipeline_quotidien` : `generer_trajets` → `analyser_heures_pointe` (soumission d'un job Spark au cluster via le SDK Docker, depuis le conteneur Airflow qui n'a pas de Java) → `verifier_resultats` (vérification des fichiers Parquet dans MinIO via boto3) → `notifier`.
6. Démonstration des retries : modification volontaire de `verifier_resultats` pour qu'elle échoue, observation des 2 tentatives de retry (30s d'intervalle), passage en `failed`, puis `notifier` en `upstream_failed`.
7. Réparation du code, `Clear` de la tâche en échec, et reprise automatique du pipeline jusqu'au succès complet.

## Réflexion personnelle

Ce TP m'a permis de comprendre concrètement pourquoi un simple `cron` ne suffit pas dès qu'un pipeline dépasse une étape isolée. Ce que j'ai le plus retenu :

- **L'idempotence** est le concept clé qui rend les retries et les backfills sûrs : si `verifier_resultats` avait eu un effet de bord cumulatif (par exemple un `append` plutôt qu'un `overwrite`), le retry automatique aurait pu créer des doublons silencieux. Le fait que Spark écrive en `overwrite` dans `anfa-processed` rend la tâche rejouable sans risque.
- **La séparation des responsabilités entre Airflow et Spark** était un point que je n'avais pas anticipé : l'image Airflow n'a pas de Java, donc `spark-submit` ne peut pas y tourner directement. La solution — piloter `docker exec` sur le conteneur Spark Master depuis Airflow via le SDK Docker — montre bien qu'un orchestrateur ne fait pas tout lui-même, il délègue et surveille.
- **La reprise après échec** (`Clear` sur la tâche rouge plutôt que tout relancer) est à mes yeux l'argument le plus concret en faveur d'un orchestrateur par rapport à un script séquentiel classique : en production, on ne veut jamais regénérer des trajets déjà générés juste parce qu'une vérification a échoué plus loin dans la chaîne.

## Difficultés rencontrées

- **Remote `upstream` non déclaré** : `git fetch upstream` échouait avec `fatal: 'upstream' does not appear to be a git repository`. Résolu en ajoutant le remote manuellement avec `git remote add upstream https://github.com/denisakp/cloud-bigdata-anfa-resources.git`.
- **Conflit avec la stack de la séance 5** : les conteneurs Spark/MinIO de la séance précédente tournaient encore et occupaient les mêmes ports. Résolu avec `docker compose down` dans `seance-05/` avant de lancer la stack de la séance 6.
- **Incompatibilité de l'image `postgres:18-alpine`** : le conteneur `anfa-postgres` refusait de démarrer (`unhealthy`) avec l'erreur *"these Docker images are configured to store database data in a format which is compatible with pg_ctlcluster"* — un changement de convention de stockage introduit en Postgres 18, incompatible avec le montage classique du volume sur `/var/lib/postgresql/data` utilisé dans le `docker-compose.yml` fourni. Résolu en substituant l'image par `postgres:16-alpine`, après un `docker compose down -v` pour repartir sur un volume propre.
- **Échec de connexion à l'UI Airflow** (`Invalid login`) malgré un utilisateur `admin` correctement créé selon les logs de `anfa-airflow-init`. Résolu en supprimant puis recréant l'utilisateur explicitement via la CLI (`airflow users delete` puis `airflow users create`), et en retentant la connexion en navigation privée pour éliminer tout résidu de session d'un ancien TP Airflow sur le même port.

## Exercices

**Exercice 1 — Point de vérification 2 (DAG `hello_anfa`)**
Le DAG a été déclenché manuellement, les 2 tâches (`dire_bonjour`, `lister_lignes`) sont passées en succès (vert foncé). Voir `captures/hello-anfa-graph.png`.

**Exercice 2 — Point de vérification 3 (DAG métier complet)**
Les 4 tâches (`generer_trajets`, `analyser_heures_pointe`, `verifier_resultats`, `notifier`) se sont exécutées avec succès dans l'ordre attendu, avec soumission effective d'un job Spark au cluster observable sur l'UI Spark (`localhost:8090`). Voir `captures/pipeline-anfa-graph.png`.

**Exercice 3 — Logs de `verifier_resultats`**
Les logs confirment la détection des fichiers Parquet produits par le job Spark dans le bucket `anfa-processed`. Voir `captures/logs-verifier-resultats.png`.

**Exercice 4 — Point de vérification 4 (retries)**
Après modification volontaire de `verifier_resultats` pour lever une `ValueError`, Airflow a retenté l'exécution 2 fois (conformément à `default_args["retries"] = 2`) avant de marquer la tâche `failed`, puis `notifier` en `upstream_failed` car sa dépendance n'a pas réussi. Voir `captures/retry-failed.png`.

## Conclusion

La stack a été correctement redémarrée avec `docker compose down` en fin de séance. La branche `seance-06` contient les DAGs, scripts, le `docker-compose.yml` (avec l'ajustement Postgres 16), le présent `RENDU.md` et les 5 captures d'écran.