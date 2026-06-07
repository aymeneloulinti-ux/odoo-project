# Mini ERP – Gestion de Stock (Core System)

## Description

Mini ERP – Gestion de Stock est un mini système ERP backend développé en Python avec une base de données SQL (PostgreSQL ou équivalent). Il constitue un noyau de gestion de stock simple, extensible et inspiré des architectures ERP comme Odoo.

Le système se concentre sur une architecture modulaire et maintenable, avec une séparation claire des responsabilités entre les données, la logique métier et les extensions.

## Objectif du projet

- Créer un noyau de gestion de stock simple mais extensible
- Permettre une évolution vers d’autres modules métiers (facturation, achats, ventes, reporting)
- Garantir la traçabilité complète des opérations de stock
- Centraliser les opérations via un service métier
- Calculer le stock uniquement à partir des mouvements, sans stockage direct du niveau de stock

## Principes architecturels

- Séparation des responsabilités : données / logique métier / extensions
- Traçabilité complète des opérations de stock
- Architecture modulaire et extensible
- Centralisation des opérations via un service métier
- Le stock est calculé à partir des mouvements, pas stocké directement

## Modèle de données

### Table `products`

- `id` (PK)
- `name` (string)
- `unit_price` (float)
- `created_at` (date)

### Table `stock_moves`

- `id` (PK)
- `product_id` (FK vers `products`)
- `type` (ENUM : `IN` / `OUT`)
- `quantity` (int)
- `date` (date)
- `reason` (string)
- `source_module` (string ou enum indiquant l’origine du mouvement)

## Logique métier

- Le stock est calculé dynamiquement :
  `Stock = somme des IN - somme des OUT`
- Une sortie de stock (`OUT`) ne peut pas être validée si le stock est insuffisant
- Toutes les opérations de stock passent par une fonction centrale :
  `create_stock_move(product_id, quantity, type, source_module)`

## Source Module

Le champ `source_module` identifie l’origine du mouvement :

- `manual` (ajustement manuel)
- `invoice` (facture client)
- `purchase` (commande fournisseur)
- `sales` (commande client)
- `adjustment` (correction inventaire)

## Architecture future (extensibilité)

Le projet est conçu pour accueillir des modules futurs :

### Module Facturation

- génération de factures clients
- création automatique de mouvements `OUT`

### Module Achats

- gestion des commandes fournisseurs
- création automatique de mouvements `IN`

### Module Ventes

- gestion des commandes clients
- réservation de stock
- conversion en facture

### Module Reporting

- statistiques de ventes
- produits les plus vendus
- analyse des mouvements de stock

### Module Inventaire

- ajustements physiques
- gestion multi-entrepôts

## Philosophie du projet

- Un produit est une donnée stable
- Un stock est une conséquence de mouvements
- Toute action métier génère un `stock_move`
- Le système est conçu pour être simple, scalable et proche d’un ERP réel

## Conclusion

Ce projet est un mini ERP backend centré sur la gestion de stock. Il offre un noyau extensible permettant d’intégrer progressivement plusieurs modules métiers tout en gardant une architecture propre et maintenable.