import requests


def update_prices():
    url = "https://api.auragold.in/api/data/v1/cron/update-prices?product=24KGOLD"
    response = requests.get(url)
    if response.status_code == 200:
        print("Prices updated successfully")
    else:
        print("Error while updating prices")


if __name__ == "__main__":
    update_prices()
