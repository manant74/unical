"""
Script di test per verificare che l'installazione sia corretta
"""

import sys
import os

def test_imports():
    """Test che tutti i moduli si importino correttamente"""
    print("🧪 Testing imports...")

    try:
        import streamlit
        print("✅ Streamlit importato correttamente")
    except ImportError as e:
        print(f"❌ Errore importando Streamlit: {e}")
        return False

    try:
        from utils.document_processor import DocumentProcessor
        print("✅ DocumentProcessor importato correttamente")
    except ImportError as e:
        print(f"❌ Errore importando DocumentProcessor: {e}")
        return False

    try:
        from utils.llm_manager import LLMManager
        print("✅ LLMManager importato correttamente")
    except ImportError as e:
        print(f"❌ Errore importando LLMManager: {e}")
        return False

    try:
        from utils.prompts import get_prompt
        print("✅ Modulo prompts importato correttamente")
    except ImportError as e:
        print(f"❌ Errore importando modulo prompts: {e}")
        return False

    return True

def test_prompts():
    """Test che i prompts si carichino correttamente"""
    print("\n🧪 Testing prompts loading...")

    try:
        from utils.prompts import get_prompt, get_all_prompts

        # Test singolo prompt
        ali_prompt = get_prompt('ali')
        if ali_prompt and len(ali_prompt) > 0:
            print(f"✅ Prompt Alì caricato ({len(ali_prompt)} caratteri)")
        else:
            print("❌ Prompt Alì vuoto")
            return False

        believer_prompt = get_prompt('believer')
        if believer_prompt and len(believer_prompt) > 0:
            print(f"✅ Prompt Believer caricato ({len(believer_prompt)} caratteri)")
        else:
            print("❌ Prompt Believer vuoto")
            return False

        # Test tutti i prompts
        all_prompts = get_all_prompts()
        print(f"✅ Caricati {len(all_prompts)} prompts totali")

        return True
    except Exception as e:
        print(f"❌ Errore nel caricamento prompts: {e}")
        return False

def test_directories():
    """Test che le directory necessarie esistano"""
    print("\n🧪 Testing directory structure...")

    required_dirs = [
        'pages',
        'utils',
        'prompts',
        'data'
    ]

    all_exist = True
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory '{dir_name}' esiste")
        else:
            print(f"❌ Directory '{dir_name}' mancante")
            all_exist = False

    return all_exist

def test_files():
    """Test che i file principali esistano"""
    print("\n🧪 Testing required files...")

    required_files = [
        'app.py',
        'requirements.txt',
        '.env.example',
        'README.md',
        'NewFeatures.md',
        'prompts/ali_system_prompt.md',
        'prompts/believer_system_prompt.md',
        'utils/document_processor.py',
        'utils/llm_manager.py',
        'utils/prompts.py'
    ]

    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File '{file_path}' esiste")
        else:
            print(f"❌ File '{file_path}' mancante")
            all_exist = False

    return all_exist

def test_env_setup():
    """Test configurazione environment"""
    print("\n🧪 Testing environment setup...")

    if os.path.exists('.env'):
        print("✅ File .env presente")

        # Verifica che almeno una API key sia configurata
        try:
            from dotenv import load_dotenv
            load_dotenv()

            has_api_key = False
            for key in ['GOOGLE_API_KEY', 'ANTHROPIC_API_KEY', 'OPENAI_API_KEY']:
                if os.getenv(key):
                    print(f"✅ {key} configurata")
                    has_api_key = True

            if not has_api_key:
                print("⚠️  Nessuna API key configurata - gli agenti non funzioneranno")
                print("   Configura almeno una API key nel file .env")
        except ImportError:
            print("❌ python-dotenv non installato")
            return False
    else:
        print("⚠️  File .env non trovato")
        print("   Copia .env.example in .env e configura le API keys")

    return True

def main():
    """Esegue tutti i test"""
    print("=" * 60)
    print("🚀 BDI Framework - Test di Setup")
    print("=" * 60)

    results = []

    # Esegui tutti i test
    results.append(("Import dei moduli", test_imports()))
    results.append(("Caricamento prompts", test_prompts()))
    results.append(("Struttura directory", test_directories()))
    results.append(("File richiesti", test_files()))
    results.append(("Configurazione environment", test_env_setup()))

    # Riepilogo
    print("\n" + "=" * 60)
    print("📊 Riepilogo Test")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "=" * 60)
    if passed == total:
        print(f"🎉 Tutti i test passati! ({passed}/{total})")
        print("\n✨ Il sistema è pronto per l'uso!")
        print("   Esegui: streamlit run app.py")
    else:
        print(f"⚠️  {passed}/{total} test passati")
        print("\n🔧 Correggi gli errori prima di procedere")
        print("   Installa le dipendenze: pip install -r requirements.txt")
        print("   Configura le API keys: copia .env.example in .env")
    print("=" * 60)

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
