import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    if "--visual" in sys.argv:
        from run_visual import run
    else:
        from run_headless import run

    run()
