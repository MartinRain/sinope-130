# Neviweb130 – revue rapide et bonnes pratiques Home Assistant 2025

## Points à améliorer

1. **Configuration mutable globale** : les options du config entry sont copiées dans des variables globales (`SCAN_INTERVAL`, `HOMEKIT_MODE`, etc.). Une autre entrée (ou un rechargement) écraserait ces valeurs pour toutes les entités. Home Assistant recommande de conserver la configuration dans `hass.data[DOMAIN]` ou dans un `DataUpdateCoordinator` par entrée. 【F:custom_components/neviweb130/__init__.py†L172-L241】
2. **Journalisation hors du contrôle de HA** : l’intégration crée et gère un fichier de log (`neviweb130_log.txt`) directement, ce qui contourne la configuration de logs de Home Assistant et peut poser des problèmes en sandbox/OS intégrés. Il est préférable d’utiliser uniquement `_LOGGER` et la configuration de logs standard de HA. 【F:custom_components/neviweb130/__init__.py†L178-L197】
3. **Code d’API intégré à l’intégration** : le client Neviweb130 mélange des appels bloquants `requests` et des appels asynchrones `aiohttp`, déclenchés via `run_coroutine_threadsafe` depuis un thread d’executor. Les bonnes pratiques HA 2025 encouragent l’utilisation d’une bibliothèque PyPI dédiée (entièrement async) et l’usage de `DataUpdateCoordinator` pour la mise à jour des données, afin d’éviter les accès réseau bloquants dans le core. 【F:custom_components/neviweb130/__init__.py†L281-L369】【F:custom_components/neviweb130/__init__.py†L390-L467】
4. **Flux de config minimal** : le `config_flow` crée l’entrée sans valider les identifiants ni proposer d’options, ce qui limite le feedback utilisateur et empêche de récupérer des erreurs d’authentification avant création. Ajouter une étape de validation (appel API test) et un flux d’options aligné sur la configuration (scan interval, notifications, etc.) faciliterait l’usage. 【F:custom_components/neviweb130/config_flow.py†L15-L40】
5. **Variables globales reprises dans les plateformes** : les plateformes (ex. `sensor.py`) importent `SCAN_INTERVAL` et d’autres indicateurs via import global. Le passage par un coordinateur par entrée permettrait d’éviter les dérives en cas de multi-gateway et de centraliser la planification des mises à jour. 【F:custom_components/neviweb130/sensor.py†L34-L107】

## Recommandations prioritaires

- Introduire un client PyPI asynchrone (ou au minimum rendre `Neviweb130Client` entièrement async) et l’injecter dans un `DataUpdateCoordinator` par config entry pour orchestrer les lectures/écritures.
- Remplacer les variables globales de configuration par un stockage par entrée (`hass.data[DOMAIN][entry_id]`) et relayer les paramètres aux entités via le coordinateur.
- Supprimer la gestion de fichier de log personnalisé et s’appuyer uniquement sur `_LOGGER`, en documentant le `logger:` à ajouter dans `configuration.yaml` pour les besoins de debug.
- Enrichir le `config_flow` avec une validation des identifiants et une `OptionsFlow` pour les paramètres modifiables (scan interval, notifications, réseaux secondaires).
