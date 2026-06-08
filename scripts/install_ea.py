"""Copy the MQL5 EA to the correct MT5 Experts folder.

Usage:
    python scripts/install_ea.py

The script:
  1. Connects to MT5 to find the terminal data path
  2. Copies mql5/smc_ai_dashboard.mq5 → MQL5/Experts/
  3. Prints instructions for compiling and attaching the EA
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False


def main() -> None:
    if not MT5_AVAILABLE:
        print("❌  pip install MetaTrader5 first.")
        sys.exit(1)

    # Connect (use already-open terminal)
    if not mt5.initialize():
        code, msg = mt5.last_error()
        print(f"❌  MT5 not reachable ({code}: {msg})")
        print("    → Open MetaTrader 5 first, then run this script.")
        sys.exit(1)

    info = mt5.terminal_info()
    data_path = Path(info.data_path)
    mt5.shutdown()

    # Paths
    src = Path(__file__).parent.parent / "mql5" / "smc_ai_dashboard.mq5"
    dst_dir = data_path / "MQL5" / "Experts"
    dst = dst_dir / "smc_ai_dashboard.mq5"

    if not src.exists():
        print(f"❌  EA source not found: {src}")
        sys.exit(1)

    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    print(f"""
✓ EA installé avec succès !

  Source : {src}
  Dest   : {dst}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Étapes suivantes dans MetaTrader 5 :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. Ouvrir MetaEditor  →  Outils → MetaEditor  (F4)

  2. Dans l'arborescence à gauche :
       Expert Advisors → smc_ai_dashboard

  3. Compiler  →  F7
     (tu dois voir "0 erreurs" en bas)

  4. Revenir sur MT5, ouvrir le graphique EURUSD.s H4

  5. Glisser l'EA depuis :
       Navigateur → Expert Advisors → smc_ai_dashboard

  6. Dans les paramètres de l'EA :
       ✓ Autoriser le trading automatique
       ✓ Autoriser les imports de DLL
     → OK

  7. Lancer le bridge Python dans un terminal :
       python -m smc_ai.cli live --symbol EURUSD.s --login 2000529599 --server JustMarkets-Demo

  Le panel apparaît sur le graphique et se met à jour
  toutes les 10 secondes automatiquement.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


if __name__ == "__main__":
    main()
