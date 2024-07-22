# -------------------------------- FastAPI imports ---------------------------
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from fastapi.openapi.utils import get_openapi

# -------------------------------- Starlette imports ---------------------------
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware


from security.settings import settings

from tags.users.routes import user_router
from tags.projects.routes import project_router
from tags.metadata.routes import table_router



app = FastAPI()

add_pagination(app)

# including routers
app.include_router(user_router)
app.include_router(project_router)
app.include_router(table_router)



# Static Files configurations
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static/templates")


# It should be changed from * to all our frontend domains
ALLOWED_ORIGINS = ["*"]

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)



# ## custom headers for api endpoints
# def add_custom_headers():

#     openapi_schema = get_openapi(
#         title="LCP",
#         description="LCP_V2 -- Community & Pro -- OpenAPI Spec (Swagger_UI)",
#         version="v2",
#         routes=app.routes,
#         terms_of_service="https://www.LCP.com/",
#         contact={
#             "name": "Visit LCP",
#             "url": "https://www.LCP.com/",
#             "email": "info@LCP.com",
#         },
#         license_info={
#             "name": "LCP License",
#             "url": "https://www.LCP.com/",
#         },
#     )

#     app.openapi_schema = openapi_schema

#     # paths = openapi_schema["paths"]
#     # for url, methods in paths.items():
#     #     # if any(path in url.split("/") for path in ["signup", "login", "forgot_password", "verify"]):
#     #     #     for method in methods:
#     #     #         if methods[method].get("parameters"):
#     #     #             methods[method]["parameters"].insert(0, LCP_flavor_header)
#     #     #         else:
#     #     #             methods[method]["parameters"] = [LCP_flavor_header]
#     #     # else:
#     #     for method in methods:
#     #         if methods[method].get("parameters"):
#     #             # methods[method]["parameters"].insert(0, authentication_header)
#     #             methods[method]["parameters"].insert(0, LCP_flavor_header)
#     #         else:
#     #             methods[method]["parameters"] = [LCP_flavor_header]

#     return app.openapi_schema





