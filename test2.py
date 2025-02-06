import httpx
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request

# Google reCAPTCHA keys (replace with your own)
SITE_KEY = "6Le9sc0qAAAAALMt_csagCKmkNPqF8_XnPkmBZO9"
SECRET_KEY = "6Le9sc0qAAAAANiVrXK5uQfCEgUaGc62hmJ1CKow"

async def verify_recaptcha(response_token: str):
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": SECRET_KEY,
        "response": response_token
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=data)
        result = r.json()
        return result.get("success", False)

async def form(request: Request):
    return HTMLResponse("""
        <form method="POST">
            <input type="text" name="name" placeholder="Enter your name" required><br>
            <div class="g-recaptcha" data-sitekey="{}"></div><br>
            <button type="submit">Submit</button>
        </form>
        <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    """.format(SITE_KEY))

async def submit(request: Request):
    form_data = await request.form()
    name = form_data.get("name")
    recaptcha_response = form_data.get("g-recaptcha-response")

    if await verify_recaptcha(recaptcha_response):
        return JSONResponse({"message": f"Hello {name}, your reCAPTCHA was successful!"})
    else:
        return JSONResponse({"error": "Invalid reCAPTCHA. Please try again."}, status_code=400)

app = Starlette(
    debug=True,
    routes=[
        Route("/", form),
        Route("/", submit, methods=["POST"]),
    ]
)

# Middlewares for security (optional)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

