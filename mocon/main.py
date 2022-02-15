# -*- coding: utf-8 -*-
from typing import List, Type

from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Router, Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.templating import Jinja2Templates

from mocon.forms import BaseForm

__all__ = ["Mocon"]

from mocon.model import BaseModel


class BaseMocon:
    def __init__(
        self,
        app: Starlette,
        base_url: str = "/mocon",
        title: str = "Mocon",
    ) -> None:
        self.app = app
        self.base_url = base_url
        self._models: List["BaseModel"] = []
        self.templates = Jinja2Templates(directory="templates")
        self.templates.env.loader = ChoiceLoader(
            [
                FileSystemLoader("templates"),
                PackageLoader("mocon", "templates"),
            ]
        )
        self.templates.env.globals["min"] = min
        self.templates.env.globals["admin_title"] = title

    @property
    def models(self) -> List["BaseModel"]:
        return self._models

    def _find_model(self, identify: str) -> "BaseModel":
        for model in self.models:
            if model.identify == identify:
                return model

        raise HTTPException(status_code=404)

    def _not_found_response(self, request: Request) -> Response:
        context = {"request": request, "status_code": 404, "message": "Not found."}
        return self.templates.TemplateResponse("error.html", context, status_code=404)

    def _unauthorized_response(self, request: Request) -> Response:
        context = {"request": request, "status_code": 401, "message": "Unauthorized."}
        return self.templates.TemplateResponse("error.html", context, status_code=401)

    def register(self, model: Type["BaseModel"]) -> None:
        self._models.append((model()))


class Mocon(BaseMocon):
    """
    app = FastAPI()
    mocon = Mocon(app, base_url="/config")

    router = APIRouter()
    mocon = Mocon(router)
    from pydantic import BaseModel
    frm mocon import BaseModel

    class Movie(BaseModel):
        class Meta:
            model_name = "movie"

        title: str
        year: int

    class MovieForm(BaseForm):
        model = Movie
        name = "电影配置"
        can_delete = False

    mocon.register(MovieForm, endpoint="/movie")
    """

    def __init__(
        self,
        app: Starlette,
        base_url: str = "/mocon",
        title: str = "Mocon",
    ) -> None:
        super().__init__(app, base_url, title)
        statics = StaticFiles(packages=["sqladmin"])
        router = Router(
            routes=[
                Mount("/statics", app=statics, name="statics"),
                Route("/", endpoint=self.index, name="index"),
                Route("/{identity}", endpoint=self.detail, name="detail"),
                Route(
                    "/{identity}/edit",
                    endpoint=self.edit,
                    name="edit",
                    methods=["POST"],
                ),
                Route(
                    "/{identity}/delete",
                    endpoint=self.delete,
                    name="delete",
                    methods=["DELETE"],
                ),
            ]
        )

        self.app.mount(base_url, router, name="mocon")
        self.templates.env.globals["models"] = self.models

    def index(self, request: Request) -> Response:
        """Index route which can be override to create dashboards."""
        context = {
            "request": request,
            "models": self.models,
        }
        return self.templates.TemplateResponse("index.html", context)

    def detail(self, request: Request) -> Response:
        model = self._find_model(request.path_params["identity"])
        if not model.Meta.can_view:
            return self._unauthorized_response(request)

        context = {
            "request": request,
        }
        return self.templates.TemplateResponse("detail.html", context)

    def edit(self, request: Request) -> Response:
        pass

    def delete(self, request: Request) -> Response:
        pass
