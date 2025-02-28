from sanic import Sanic
from sanic_cors import CORS

from api.settings import SANIC_CONFIG

app = Sanic("CodingInterviewQuestionsApp")
app.config.update(SANIC_CONFIG)
CORS(app, resources={r"/*": {"origins": app.config.DOMAIN}})
