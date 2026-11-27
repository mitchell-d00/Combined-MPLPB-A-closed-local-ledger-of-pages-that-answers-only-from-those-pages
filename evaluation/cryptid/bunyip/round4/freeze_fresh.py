"""Freeze the second arm with its versioned evaluation coordinate adapter."""
import argparse
from pathlib import Path

import packet

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key',type=Path,required=True)
    args=parser.parse_args()
    packet.HARNESS += tuple(str((packet.HOME/name).relative_to(packet.ROOT))
                            for name in ('score_v2.py','freeze_fresh.py','REPAIR.md'))
    packet.make('fresh',args.key)
