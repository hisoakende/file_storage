import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.absolute()

sys.path.insert(0, str(project_root))
