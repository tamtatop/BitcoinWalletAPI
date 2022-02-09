from httpx import Response, request

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8080


API_QUERIES = [
    ("POST", "/users"),
    ("POST", "/wallets"),
    ("GET", "/wallets/{address}"),
    ("POST", "/transactions"),
    ("GET", "/transactions"),
    ("GET", "/wallets/{address}/transactions"),
    ("GET", "/statistics"),
]


class Requester:
    method_get = "GET"
    method_post = "POST"
    method_head = "HEAD"

    def __init__(self, *, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        self.host = host
        self.port = port

    def request(self, method: str, query: str) -> Response:
        url = f"http://{self.host}:{self.port}{query}"
        return request(method, url)


def test_each_url() -> None:
    requester = Requester()

    for method, query in API_QUERIES:
        if "{address}" in query:
            query = query.replace("{address}", "_")

        response: Response = requester.request(method, query)
        assert response.status_code == 200
