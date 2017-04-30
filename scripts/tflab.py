import site
from os.path import dirname
site.addsitedir(dirname((dirname(__file__))))

import sys
from tensorlab.ui import cli
sys.exit(cli.main())
