import subprocess
import sys
import os

def main():
    """Launch the AeroMix frontend"""
    print("🎵 Launching AeroMix Frontend...")
    
    # Check if required files exist
    required_files = [
        "utils/gesture_Detection.py",
        "ml/classifier.py",
        "sound_control.py",
        "utils/osc_handler.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend_app.py", 
            "--server.port=8501",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Error launching frontend: {e}")

if __name__ == "__main__":
    main()
