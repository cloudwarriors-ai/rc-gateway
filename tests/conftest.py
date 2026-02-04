import sys
from pathlib import Path

# Add the app directory to the Python path for tests
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))