"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""


activate_this = '/path/to/virtualenv/cli-mate2/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from climate import app as application