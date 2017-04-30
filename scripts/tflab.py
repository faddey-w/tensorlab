import site
from os.path import dirname
site.addsitedir(dirname((dirname(__file__))))

import sys
from tensorlab.interfaces import cli
sys.exit(cli.main())
