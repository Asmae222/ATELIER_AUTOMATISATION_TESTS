# API Choice

- **Étudiant** : (ton nom)
- **API choisie** : Frankfurter
- **URL base** : https://api.frankfurter.app
- **Documentation officielle** : https://frankfurter.dev
- **Auth** : None

## Endpoints testés

- `GET /latest` — taux de change du jour (base EUR)
- `GET /latest?from=EUR` — taux depuis EUR
- `GET /latest?from=USD&to=GBP` — conversion USD → GBP
- `GET /2020-01-01` — taux historique à une date précise
- `GET /currencies` — liste de toutes les devises supportées
- `GET /latest?from=ZZZZ` — cas invalide → erreur attendue
- `GET /2999-01-01` — date future → réponse gérée sans crash

## Hypothèses de contrat

| Champ | Type | Obligatoire |
|-------|------|-------------|
| `amount` | float | ✅ |
| `base` | string (ex: "EUR") | ✅ |
| `date` | string ISO (YYYY-MM-DD) | ✅ |
| `rates` | object (dict devise→float) | ✅ |

- HTTP 200 sur tous les endpoints valides
- `rates` non vide (> 0 devises)
- Erreur 400/404/422 sur devise invalide

## Limites / rate limiting connu

- Pas de limite documentée explicitement
- Bonne pratique : ≤ 1 run / 5 min, ≤ 20 requêtes / run

## Risques

- Dépend de la BCE (Banque Centrale Européenne) pour les données
- Pas de taux le week-end (dernière date de semaine retournée)
- Possible downtime ponctuel du service
