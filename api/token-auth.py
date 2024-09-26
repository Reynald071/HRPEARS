import requests


def client():
    token_h = "Token 82b88a7bdac1ea3868361448927035e93b0dc19d"
    credentials = {"username": "pecmonares", "password": "Bally@120717"}

    response = requests.post("https://caraga-portal.dswd.gov.ph/api/rest-auth/login/",
                             data=credentials, verify=False)
    headers = {"Authorization": token_h}
    response_data = response.json()


if __name__ == "__main__":
    client()