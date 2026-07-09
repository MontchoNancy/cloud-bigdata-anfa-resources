# RENDU – Séance 7 : Streaming et architectures événementielles avec Kafka

**Nom :** MONTCHO Nancy
**Identifiant GitHub :** MontchoNancy
**Formation :** Master 1 IABD – ESGIS
**Cours :** Cloud & Big Data – Denis AKPAGNONITE

---

## Résumé

Cette séance avait pour objectif de faire passer la plateforme Anfa d'un traitement par lots (batch), utilisé depuis les séances 1 à 6, à un traitement en flux continu (streaming). J'ai déployé un cluster Kafka à 3 brokers en mode KRaft (sans Zookeeper), accompagné de Kafka UI pour l'observation, MinIO pour le stockage, et un cluster Spark (1 master, 1 worker) pour la consommation du flux.

J'ai créé le topic `anfa-positions-bus` (3 partitions, réplication factor 3), testé l'envoi et la lecture de messages avec un producer et un consumer Python simples, puis lancé le simulateur de flotte représentant 100 bus Anfa envoyant leur position GPS en continu (~100 messages/seconde). J'ai ensuite volontairement arrêté un broker (`anfa-kafka-2`) pour observer la tolérance aux pannes du cluster, avant de le redémarrer.

Enfin, j'ai consommé le flux Kafka avec Spark Structured Streaming : d'abord un job simple affichant les messages bruts en console, puis un job d'agrégation calculant, toutes les 30 secondes, le nombre de bus actifs par ligne et leur vitesse moyenne, avec écriture des résultats au format Parquet dans MinIO (bucket `anfa-streaming`).

Le pipeline complet fonctionne de bout en bout : simulateur → Kafka (3 brokers) → Spark Structured Streaming → agrégation en fenêtre → MinIO.

---

## Étapes principales

1. **Récupération des fichiers et création de la branche** : synchronisation du fork avec le dépôt du cours (`upstream/main`), création de la branche `seance-07`.
2. **Déploiement du cluster Kafka (KRaft, 3 brokers)** : lancement via `docker compose up -d`, vérification des 3 brokers actifs dans Kafka UI.
3. **Création du topic** `anfa-positions-bus` (3 partitions, réplication factor 3) via Kafka UI.
4. **Producer/consumer Python simples** : installation de `kafka-python`, exécution de `premier_producer.py` et `premier_consumer.py`, vérification des messages et de la garantie d'ordre par clé (`bus_id`).
5. **Simulation de la flotte** : lancement de `simulateur_flotte.py`, envoi continu des positions GPS de 100 bus, observation du débit croissant dans Kafka UI.
6. **Test de tolérance aux pannes** : arrêt du broker `anfa-kafka-2` (`docker stop`), vérification que le simulateur continue d'envoyer sans erreur et que le cluster reste disponible avec 2 brokers sur 3, puis redémarrage du broker.
7. **Spark Structured Streaming – lecture console** : soumission du job `lecture_flux_console.py`, affichage des micro-batchs de positions parsées.
8. **Préparation de MinIO** : création de la clé applicative `anfa-app-key` et du bucket `anfa-streaming`.
9. **Spark Structured Streaming – agrégation** : soumission du job `agregation_streaming.py`, calcul du nombre de bus actifs et de la vitesse moyenne par ligne sur des fenêtres de 30 secondes, écriture des résultats en Parquet dans `anfa-streaming/agregats_par_ligne/`.
10. **Arrêt propre** de la stack (`docker compose down`) et rédaction du présent RENDU.

---

## Difficultés rencontrées

- **Redémarrage du cluster Docker en cours de route** : à un moment, les conteneurs Kafka sont devenus inaccessibles depuis mes scripts Python (`KafkaTimeoutError: Unable to bootstrap from [...]`). Un simple redémarrage de la stack (`docker compose up -d`) a résolu le problème.
- **Cluster Spark bloqué avec un seul cœur disponible** : mon worker Spark ne dispose que d'1 seul cœur (`Cores in use: 1 Total`). Après avoir fermé un terminal sans arrêter proprement un job Spark (fermeture directe de la fenêtre au lieu d'un `Ctrl+C`), l'application est restée active côté cluster (statut `RUNNING`) et a monopolisé l'unique cœur disponible. Le job suivant restait alors bloqué en `WAITING` avec le message `Initial job has not accepted any resources`. La solution a été d'aller sur l'interface Spark Master (`http://localhost:8091`) et de tuer manuellement (`kill`) les applications fantômes encore actives avant de relancer un nouveau job. Cela m'a appris à toujours arrêter un job Spark avec `Ctrl+C` dans son terminal plutôt que de fermer la fenêtre directement.
- **Ordre des captures d'écran** : j'ai oublié dans un premier temps de faire la capture de la Partie 5 (tolérance aux pannes, 2 brokers sur 3) en enchaînant directement vers la partie Spark. Je l'ai reprise après coup, une fois le simulateur relancé.

---

## Points de vérification validés

- [x] Point de vérification 1 : 3 brokers Kafka actifs, visibles dans Kafka UI.
- [x] Point de vérification 2 : topic `anfa-positions-bus` créé avec 3 partitions, chacune répliquée sur 3 brokers.
- [x] Point de vérification 3 : messages Kafka envoyés et lus avec mes propres scripts Python ; compréhension du rôle du `group_id` et des offsets.
- [x] Point de vérification 4 : simulateur lancé, ~100 messages/seconde envoyés, visibles en direct dans Kafka UI.
- [x] Point de vérification 5 : cluster Kafka observé survivant à la perte d'un broker, sans interruption ni perte de message.
- [x] Point de vérification 6 (final) : pipeline complet fonctionnel : simulateur → Kafka (3 brokers) → Spark Structured Streaming → agrégation en fenêtre → MinIO.

---

## Réflexion personnelle

Cette séance marque un vrai changement de paradigme par rapport aux séances précédentes : on ne traite plus un fichier complet une fois par jour, mais un flux sans fin, dont on ne connaît jamais la taille à l'avance. Ce qui m'a le plus marqué, c'est le découplage total entre producteur et consommateur : le simulateur de bus n'a aucune idée de qui lit ses messages, ni combien de lecteurs il y a — exactement le problème que rencontrait Kossi avec son script direct vers MinIO.

L'expérience de tuer un broker en pleine simulation a rendu concret un concept qu'on aurait pu voir comme purement théorique : la réplication à 3 exemplaires a vraiment permis au cluster de continuer à fonctionner sans que le simulateur ne s'en aperçoive. Le point le plus formateur a cependant été la gestion des ressources Spark : avec un seul cœur disponible, j'ai compris de façon très concrète pourquoi il faut toujours arrêter proprement un job avant d'en lancer un autre, sous peine de bloquer tout le cluster avec une application fantôme.

---

## Captures d'écran (dossier `captures/`)

- `kafka-ui-brokers.png` — Les 3 brokers Kafka actifs dans Kafka UI.
- `kafka-ui-debit.png` — Débit de messages en augmentation pendant l'exécution du simulateur.
- `kafka-ui-2-brokers.png` — 2 brokers actifs sur 3 après l'arrêt volontaire de `anfa-kafka-2`.
- `spark-streaming-console.png` — Micro-batchs affichés en console par le job `lecture_flux_console.py`.
- `minio-agregats.png` — Fichiers Parquet générés par le job d'agrégation dans le bucket `anfa-streaming/agregats_par_ligne/`.