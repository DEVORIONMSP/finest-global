"""
Script d'initialisation : crée toutes les tables dans la base de données
et injecte les catégories de produits et de services par défaut.
"""

from database import engine, Base, SessionLocal
import models
from models import Category

def init_database():
    print("🔄 Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées !")

    print("🔄 Injection des catégories...")
    db = SessionLocal()

    try:
        # Vérifier si des catégories existent déjà
        if db.query(Category).count() == 0:
            
            # ==========================================
            # A. CATÉGORIES DE PRODUITS
            # ==========================================
            product_categories = [
                {"name": "Fashion & Accessories", "desc": "Clothing, shoes, bags, jewellery", "emoji": "👗"},
                {"name": "Beauty & Personal Care", "desc": "Hair products, cosmetics, skincare", "emoji": "💅"},
                {"name": "Home & Living", "desc": "Curtains, bedsheets, towels, furniture", "emoji": "🛋️"},
                {"name": "Electronics & Technology", "desc": "Phones, computers, accessories", "emoji": "📱"},
                {"name": "Food & Groceries", "desc": "Food items, ingredients, packaged foods", "emoji": "🍲"},
                {"name": "Health & Wellness Products", "desc": "Personal care and wellness goods", "emoji": "💊"},
                {"name": "Baby & Children’s Products", "desc": "Toys, clothing, children’s accessories", "emoji": "👶"},
                {"name": "Building & Home Improvement", "desc": "Building materials, tools, fittings", "emoji": "🧱"},
                {"name": "Business & Office Supplies", "desc": "Stationery, office equipment", "emoji": "📎"},
                {"name": "Other Products", "desc": "Products that don’t fit the categories above", "emoji": "📦"},
            ]

            # ==========================================
            # B. CATÉGORIES DE SERVICES
            # ==========================================
            service_categories = [
                {"name": "Beauty & Personal Care", "desc": "Hair braiding, hairstyling, barbering, makeup, nail care", "emoji": "💇‍♀️"},
                {"name": "Vehicle Services", "desc": "Mechanics, auto electricians, car washing, tyre repairs", "emoji": "🚗"},
                {"name": "Home & Repair Services", "desc": "Plumbing, electrical work, carpentry, painting", "emoji": "🔧"},
                {"name": "Food Preparation & Processing", "desc": "Grinding ingredients, food processing, catering, baking", "emoji": "👨‍🍳"},
                {"name": "Cleaning & Laundry", "desc": "House cleaning, commercial cleaning, laundry, ironing", "emoji": "🧹"},
                {"name": "Fashion & Tailoring", "desc": "Tailoring, alterations, fashion design", "emoji": "🧵"},
                {"name": "Photography & Events", "desc": "Photography, videography, event decoration, event planning", "emoji": "📸"},
                {"name": "Transport & Delivery", "desc": "Moving services, local transport, delivery providers", "emoji": "🚚"},
                {"name": "Education & Training", "desc": "Tutors, language teachers, professional training", "emoji": "🎓"},
                {"name": "Digital & Technology Services", "desc": "Website development, graphic design, IT support", "emoji": "💻"},
                {"name": "Marketing & Creative Services", "desc": "Digital marketing, advertising, content creation, branding", "emoji": "📢"},
                {"name": "Business & Professional Services", "desc": "Accounting, bookkeeping, consulting, legal services", "emoji": "💼"},
                {"name": "Other Services", "desc": "Services that don’t fit the categories above", "emoji": "🛠️"},
            ]

            # Insertion des catégories de PRODUITS
            for i, cat in enumerate(product_categories):
                db.add(Category(
                    name=cat["name"],
                    type="product",
                    description=cat["desc"],
                    emoji=cat["emoji"],
                    display_order=i
                ))
            
            # Insertion des catégories de SERVICES
            for i, cat in enumerate(service_categories):
                db.add(Category(
                    name=cat["name"],
                    type="service",
                    description=cat["desc"],
                    emoji=cat["emoji"],
                    display_order=i
                ))
            
            db.commit()
            print(f"✅ {len(product_categories)} catégories de produits injectées.")
            print(f"✅ {len(service_categories)} catégories de services injectées.")
        else:
            print("ℹ️ Les catégories existent déjà, aucune injection effectuée.")

    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {e}")
        db.rollback()
    finally:
        db.close()

    print(f"📁 Fichier créé : finest_global.db")

if __name__ == "__main__":
    init_database()