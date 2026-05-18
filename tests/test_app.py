import time
import requests


def test_home_page_returns_200():
    url = "http://127.0.0.1:5000/"
    # bis zu 5 Sekunden auf Server bereit warten
    for _ in range(10):
        try:
            r = requests.get(url, timeout=1)
            assert r.status_code == 200
            return
        except Exception:
            time.sleep(0.5)
    # wenn nach Wartezeit kein Erfolg, assert fail
    assert False, "Home page did not return 200"
