import urllib

def buildURL(params):
    """Build an URL from a dictionary of parameters.

    Returns string.
    """
    base = "http://cs.joensuu.fi/~pviktor/python/signup?"
    return base + "&".join([
            "%s=%s" % (k, v)
            for k, v in params.items()
        ])

if __name__ == "__main__":
    myInfo = {
            # Please put information about yourself here
            "name": "Petr Viktorin",
            "studentno": "185052",
            "email": "encukou@gmail.com",
            "program": "IMPIT",
        }
    page = urllib.urlopen(buildURL(myInfo))
    print page.read()
