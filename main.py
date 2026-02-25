from fastapi import Request, Depends
from fastapi.responses import RedirectResponse
from authorization import is_logged
import uvicorn

from settings import app, settings, templates

app.title = "Application Interface API"
app.description = "Backend services for the application."
app.version = "1.0.0"

import api.authorization
import api.admin
import api.mobile_network
import events

@app.get("/", include_in_schema=False)
async def mainPage(request: Request):
    logged, payload = await is_logged(request, "cookies")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            **payload,
            "logged": logged
        }
    )

@app.get("/login", include_in_schema=False)
async def loginPage(request: Request):
    logged, payload = await is_logged(request, "cookies")
    if logged:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            **payload,
            "logged": logged
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings["host"],
        port=settings["port"],
        reload=settings["debug"]
    )