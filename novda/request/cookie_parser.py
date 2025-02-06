from http.cookies import SimpleCookie


def cookie_parser(cookie_string: str) -> dict[str, str]:
    cookie = SimpleCookie()
    cookie.load(cookie_string)

    return {k: v.value for k, v in cookie.items()}
