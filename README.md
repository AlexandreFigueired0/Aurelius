# Aurelius — Discord Stock Bot

Aurelius is a Discord bot that delivers live stock data, charts, news, and price alerts to your server. It’s built to be production-ready (Dockerized, CI/CD with GitHub Actions) and also serves as a portfolio‑grade project highlighting a clean Python service, a PostgreSQL schema, and an automated deployment workflow.

- Core runtime: Python 3.13, [discord.py](https://discordpy.readthedocs.io/)
- Market data: [yfinance](https://pypi.org/project/yfinance/)
- Data & plotting: pandas, matplotlib
- Persistence: PostgreSQL (psycopg2)
- Containerization: Docker (+ VS Code Dev Containers)
- CI/CD: GitHub Actions with SSH deployment to EC2

See source code in [main.py](main.py), DB layer in [database_service.py](database_service.py), database bootstrap in [utils/init_db.py](utils/init_db.py), and runner scripts in [scripts/](scripts). Ticker seeding is fetched from the SEC in [utils/collect_stocks_names.py](utils/collect_stocks_names.py).

---

## Features

- Discord commands:
  - `!hello` — basic greeting
  - `!stock <ticker|company>` — live price, % change, market cap + mini chart
  - `!info <ticker|company>` — company description, sector, industry, CEO
  - `!chart <ticker|company> [period]` — historical chart (default 1mo)
  - `!news <ticker|company>` — latest news with paginated embeds
  - `!watch <ticker|company> [threshold]` — price change alerts (default 10%)
  - `!unwatch <ticker|company>` — stop alerts
  - `!list` — list watched tickers and thresholds
  - `!metrics <ticker|company>` — key financial metrics snapshot
  - `!compare <ticker1> <ticker2> [period]` — compare two tickers
  - `!compare_sp500 <ticker> [period]` — compare a ticker vs S&P 500
  - `!help` — command reference
- Server‑scoped alerting loop with a read‑only #stock-alerts channel, powered by [`main.check_stock_percent_changes`](main.py).
- Robust ticker lookup: company name or ticker via [`database_service.get_ticker_by_name`](database_service.py).
- PostgreSQL schema and seed via [utils/init_db.py](utils/init_db.py), using SEC company tickers from [utils/collect_stocks_names.py](utils/collect_stocks_names.py) (no CSV needed).
- Docker images for bot runtime and a Dev Container for local iteration.
- Automated deploy to EC2 using [/.github/workflows/main.yml](.github/workflows/main.yml).

---

## Architecture

- Bot entrypoint: [main.py](main.py)
  - Commands, embeds, charts, news, and alert task loop [`main.check_stock_percent_changes`](main.py)
- Database service: [database_service.py](database_service.py)
  - Lookup and CRUD helpers (servers, subscriptions, thresholds)
- DB bootstrap: [utils/init_db.py](utils/init_db.py)
  - Creates tables: server, stock, subscribed_stock
  - Seeds stocks from SEC JSON via `get_ticker_name_dict()` in [utils/collect_stocks_names.py](utils/collect_stocks_names.py)
- Container entrypoint: [scripts/aurelius_entrypoint.sh](scripts/aurelius_entrypoint.sh)
  - Runs DB init then starts the bot

---

## Local Development (VS Code Dev Container)

- Open in Dev Container (uses [DevDockerfile](DevDockerfile))
- Ensure the Docker network and DB are available once:
  ```bash
  bash scripts/container_network.sh
  bash scripts/start_bd.sh
  ```
- Build and run the bot locally:
  ```bash
  bash scripts/build_bot_container.sh
  bash scripts/run_bot_container.sh
  ```

The entrypoint runs [utils/init_db.py](utils/init_db.py) to create/seed the DB, then starts the bot.

---

## Deployment (GitHub Actions → EC2)

Pushes to `main` trigger [/.github/workflows/main.yml](.github/workflows/main.yml) which:

- Builds and pushes a Docker image to Docker Hub
- SSHes into the EC2 host
- Pulls latest code/image
- Runs the bot container with the updates

Configure repository secrets:

- `DOCKER_NAME`, `DOCKER_TOKEN`
- `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`

On the EC2 host, ensure the Docker network and DB container exist (run once):

```bash
bash scripts/container_network.sh
bash scripts/start_bd.sh
```

Then the workflow’s deploy step will start the bot via:
- [scripts/run_bot_container.sh](scripts/run_bot_container.sh)

---

## Portfolio Highlights

- End‑to‑end service: Discord integration, market data ingestion, charting, alerting, and news.
- Clean Python layering: Core logic in [main.py](main.py), DB access via [`database_service`](database_service.py), schema/seed in [utils/init_db.py](utils/init_db.py).
- Data seeding from the SEC’s official ticker list (no CSV maintenance).
- Production tooling: Dockerized runtime, persistent DB volume, and CI/CD to EC2.
- Dev ergonomics: VS Code Dev Container and simple scripts for running infra locally.