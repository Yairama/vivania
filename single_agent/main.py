import sys

if __name__ == "__main__":
    if "--visual" in sys.argv:
        from run_visual import run
    else:
        from run_headless import run

    run()
