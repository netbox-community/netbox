"""Allow `python -m netbox` to behave like the `netbox` console script."""

import sys

from .cli import main

if __name__ == '__main__':
    sys.exit(main())
