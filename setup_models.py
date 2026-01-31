"""
LUMIA Studio - Setup Modelli
============================

Script per pre-scaricare i modelli necessari al funzionamento di LUMIA Studio.
Esegui questo script UNA VOLTA prima di utilizzare l'applicazione per evitare
download durante l'uso.

Uso:
    python setup_models.py

Cosa viene scaricato:
    - Modello di embedding: paraphrase-multilingual-MiniLM-L12-v2
    - Dimensioni: ~120 MB
    - Provider: HuggingFace (sentence-transformers)
"""

import sys
import os

def main():
    print("=" * 70)
    print("🚀 LUMIA Studio - Inizializzazione Modelli")
    print("=" * 70)
    print()

    # Step 1: Verifica dipendenze
    print("📦 Step 1/3: Verifica dipendenze...")
    try:
        import sentence_transformers
        print(f"   ✅ sentence-transformers {sentence_transformers.__version__}")
    except ImportError:
        print("   ❌ sentence-transformers non installato")
        print("   💡 Esegui: pip install sentence-transformers")
        sys.exit(1)

    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        print("   ✅ langchain-huggingface installato")
    except ImportError:
        print("   ❌ langchain-huggingface non installato")
        print("   💡 Esegui: pip install langchain-huggingface")
        sys.exit(1)

    print()

    # Step 2: Download modello embedding
    print("📥 Step 2/3: Download modello di embedding...")
    print("   Modello: paraphrase-multilingual-MiniLM-L12-v2")
    print("   Provider: HuggingFace")
    print("   Dimensioni: ~120 MB")
    print()
    print("   ⏳ Download in corso (potrebbe richiedere 1-2 minuti)...")
    print()

    try:
        from sentence_transformers import SentenceTransformer

        # Download del modello (mostra progress bar automaticamente)
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        print()
        print(f"   ✅ Modello scaricato con successo!")

        # Determina la cache folder
        cache_folder = None
        if hasattr(model, 'cache_folder'):
            cache_folder = model.cache_folder
        elif hasattr(model, '_cache_folder'):
            cache_folder = model._cache_folder
        else:
            # Default HuggingFace cache location
            cache_folder = os.path.expanduser("~/.cache/huggingface/hub/")

        print(f"   📁 Cache: {cache_folder}")
        print()
    except Exception as e:
        print(f"   ❌ Errore durante il download: {str(e)}")
        sys.exit(1)

    # Step 3: Test embedding
    print("🧪 Step 3/3: Test funzionalità embedding...")
    try:
        # Test con frase italiana
        test_text = "Questo è un test di embedding per LUMIA Studio"
        test_embedding = model.encode(test_text)

        print(f"   ✅ Test completato con successo!")
        print(f"   📊 Dimensioni embedding: {len(test_embedding)} dimensioni")
        print(f"   🔢 Tipo: {type(test_embedding)}")
        print()
    except Exception as e:
        print(f"   ❌ Errore durante il test: {str(e)}")
        sys.exit(1)

    # Riepilogo finale
    print("=" * 70)
    print("✅ Setup completato con successo!")
    print("=" * 70)
    print()
    print("📝 Riepilogo:")
    print(f"   • Modello: paraphrase-multilingual-MiniLM-L12-v2")
    print(f"   • Dimensioni embedding: 384")
    print(f"   • Cache locale: {cache_folder}")
    print()
    print("🎯 Prossimi passi:")
    print("   1. Avvia LUMIA Studio: streamlit run app.py")
    print("   2. Il modello sarà caricato istantaneamente dalla cache locale")
    print()
    print("💡 Note:")
    print("   • Il download è necessario solo la prima volta")
    print("   • Le sessioni successive useranno la cache locale")
    print("   • Non è necessario rieseguire questo script")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Errore imprevisto: {str(e)}")
        sys.exit(1)
