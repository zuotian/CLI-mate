"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""


from flask import Flask

app = Flask(__name__)

from . import views
