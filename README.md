sudo apt install nodejs -y
sudo apt install npm -y
npm install pm2 -g

curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"
sudo apt-get install unzip
unzip awscliv2.zip
sudo ./aws/install
aws configure

poetry config virtualenvs.in-project true
poetry install
sudo apt -y install weasyprint
poetry shell

run server: NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-config src/uvicorn_log_config.json
