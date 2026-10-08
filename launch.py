#!/usr/bin/env python3
"""Start the MPLPB local reader and open its browser front end."""
import sys
from tools.ledger_ui import main

if __name__ == '__main__':
    sys.argv.append('--open')
    main()
