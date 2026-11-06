"""
Script d'indexation : génère un vecteur (embedding) Gemini pour chaque produit
et le stocke dans la colonne `embedding` de la table `products`.
"""
import os
import time
from google import genai
from google.genai import types
from sqlalchemy import text

from database import SessionLocal
from models import Product

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("La variable d'environnement GEMINI_API_KEY n'est pas définie.")

client = genai.Client(api_key=GEMINI_API_KEY)

def get_embedding_for_product(product):
    text_content = (
        f"Produit: {product.name}. "
        f"Description: {product.description or 'aucune'}. "
        f"Catégorie: {product.category or 'non classé'}. "
        f"Couleur: {product.color or 'non spécifiée'}."
    )
    
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[text_content],
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=768
        )
    )
    
    return result.embeddings[0].values

def run_indexing():
    db = SessionLocal()
    try:
        # On récupère tous les produits
        products = db.query(Product).all()
        print(f"🔄 {len(products)} produit(s) à traiter.")
        
        count = 0
        for prod in products:
            print(f"  → Indexation de {prod.name}...")
            try:
                vecteur = get_embedding_for_product(prod)
                
                # 🆕 Mise à jour SQL directe (plus fiable avec pgvector)
                # On convertit la liste Python en string formaté pour pgvector
                vector_str = '[' + ','.join(str(x) for x in vecteur) + ']'
                
                db.execute(
                    text("UPDATE products SET embedding = CAST(:vec AS vector) WHERE id = :id"),
                    {"vec": vector_str, "id": prod.id}
                )
                db.commit()
                count += 1
                print(f"     ✅ OK ({len(vecteur)} dimensions)")
                time.sleep(0.5)
            except Exception as e:
                print(f"     ❌ Erreur : {e}")
                db.rollback()
        
        print(f"\n✅ {count} produit(s) indexé(s) avec succès.")
    finally:
        db.close()

if __name__ == "__main__":
    run_indexing()