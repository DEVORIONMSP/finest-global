"""
Migration : ajoute latitude, longitude, locality, market, code aux boutiques.
Ajoute availability aux produits.
"""

from database import SessionLocal, engine
from sqlalchemy import text
from models import Shop, Product

def migrate():
    db = SessionLocal()
    
    print("=" * 60)
    print("🔄 MIGRATION GÉOLOCALISATION")
    print("=" * 60)
    
    # ============================================================
    # 1. Ajouter les colonnes aux boutiques
    # ============================================================
    print("\n📦 Étape 1 : Ajout des colonnes aux boutiques...")
    
    with engine.connect() as conn:
        columns_shops = [
            ("latitude", "FLOAT"),
            ("longitude", "FLOAT"),
            ("locality", "VARCHAR(100)"),
            ("market", "VARCHAR(100)"),
            ("code", "VARCHAR(20)"),
            ("is_active", "BOOLEAN DEFAULT TRUE"),
        ]
        
        for col_name, col_type in columns_shops:
            try:
                conn.execute(text(f"ALTER TABLE shops ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                print(f"  ✅ shops.{col_name}")
            except Exception as e:
                print(f"  ⚠️  shops.{col_name} : {e}")
        
        conn.commit()
    
    # ============================================================
    # 2. Ajouter availability aux produits
    # ============================================================
    print("\n📦 Étape 2 : Ajout du champ availability aux produits...")
    
    with engine.connect() as conn:
        try:
            conn.execute(text(
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS availability VARCHAR(20) DEFAULT 'in_stock'"
            ))
            print("  ✅ products.availability")
        except Exception as e:
            print(f"  ⚠️  products.availability : {e}")
        conn.commit()
    
    # ============================================================
    # 3. Générer les codes pour les boutiques existantes
    # ============================================================
    print("\n📦 Étape 3 : Génération des codes boutiques...")
    
    shops = db.query(Shop).order_by(Shop.id).all()
    updated = 0
    for i, shop in enumerate(shops, start=1):
        if not shop.code:
            shop.code = f"FG-{i:04d}"
            updated += 1
    
    db.commit()
    print(f"  ✅ {updated} boutique(s) mises à jour")
    
    # ============================================================
    # 4. Migrer in_stock → availability pour les produits
    # ============================================================
    print("\n📦 Étape 4 : Migration in_stock → availability...")
    
    products = db.query(Product).all()
    updated_products = 0
    for product in products:
        if product.availability is None:
            if product.in_stock:
                product.availability = 'in_stock'
            else:
                product.availability = 'out_of_stock'
            updated_products += 1
    
    db.commit()
    print(f"  ✅ {updated_products} produit(s) mis à jour")
    
    # ============================================================
    # 5. Définir une localité par défaut
    # ============================================================
    print("\n📦 Étape 5 : Localité par défaut...")
    
    shops_without_locality = db.query(Shop).filter(Shop.locality.is_(None)).all()
    for shop in shops_without_locality:
        shop.locality = "Cotonou"
    
    db.commit()
    print(f"  ✅ {len(shops_without_locality)} boutique(s) avec localité par défaut")
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION TERMINÉE AVEC SUCCÈS")
    print("=" * 60)
    
    db.close()


if __name__ == "__main__":
    migrate()