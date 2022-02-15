# -*- coding: utf-8 -*-
import redis
import uvicorn
from starlette.applications import Starlette

from mocon.main import Mocon
from mocon.model import BaseModel

app = Starlette(debug=True)
db = redis.Redis(host='localhost', port=6379, db=0)
mocon = Mocon(app)


class FavoriteMovieModel(BaseModel):
    class Meta:
        source = db
        can_view = True

    title: str
    description: str
    director: str
    pub_year: int


mocon.register(FavoriteMovieModel)

if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=8000)
