from __future__ import annotations

import os
import sys
import argparse

# Ensure src package is on path when running the script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from database.session import engine
from models.base import Base


def import_models():
    # import modules to ensure SQLAlchemy metadata is populated
    modules = [
        'role_permission_table',
        'role',
        'permission',
        'user',
        'warehouse',
        'category',
        'product',
        'stock_movement',
    ]
    for m in modules:
        try:
            __import__(f"models.{m}", fromlist=["*"])
        except Exception:
            # ignore missing modules; metadata will include what's available
            pass


def clear_database(assume_yes: bool = False):
    import_models()

    tables = [t.name for t in Base.metadata.sorted_tables]
    if not tables:
        print("Aucune table trouvée dans le metadata; rien à vider.")
        return

    print("Tables détectées:", ", ".join(tables))

    if not assume_yes and os.environ.get('FORCE_CLEAR') != '1':
        confirm = input('CONFIRMER LA SUPPRESSION DE TOUTES LES DONNÉES (tape "yes" pour continuer): ')
        if confirm.strip().lower() != 'yes':
            print('Annulé par l\'utilisateur.')
            return

    sql = f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE;"
    with engine.begin() as conn:
        conn.execute(text(sql))

    print('Toutes les tables ont été vidées (identités réinitialisées).')


def main():
    parser = argparse.ArgumentParser(description='Clear all data from the database (destructive).')
    parser.add_argument('--yes', action='store_true', help='Do not prompt for confirmation')
    args = parser.parse_args()

    clear_database(assume_yes=args.yes)


if __name__ == '__main__':
    main()
