try:
    import edge_tts
    print(f"✅ edge-tts is installed. Version: {edge_tts.__version__ if hasattr(edge_tts, '__version__') else 'Unknown'}")
except ImportError:
    print("❌ edge-tts is NOT installed.")
