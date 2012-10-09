"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""

from climate import app

@app.route('/')
def hello_world():
    return 'Hello World!'