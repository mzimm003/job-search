from requests_html import (
    HTMLSession
)
from typing import (
    Dict
)
import requests_html

def request(searchReq:Dict):
    ses = HTMLSession()
    return ses.request(**searchReq)

def getlinks(
        webpageResp:requests_html.HTMLResponse,
        keyword:str):
        l = []
        for link in webpageResp.html.absolute_links:
            if keyword in link:
                l.append(link)
        return l