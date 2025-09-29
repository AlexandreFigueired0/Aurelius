# Aurelius — Discord Stock Bot

Aurelius is a production‑ready Discord bot that delivers real‑time stock data, charts, news, comparisons, alerts, and financial metrics directly into your server. It ships with an independently deployed marketing site and full cloud infrastructure.

Core highlights:
- **Full‑stack application**: Python Discord bot backend + React/Vite landing site
- **Cloud‑native architecture**: AWS (EC2, S3, CloudFront) with path‑scoped CI/CD
- **Advanced CI/CD**: Dual GitHub Actions pipelines (bot + website) with selective deploys
- **High performance**: Global CDN (CloudFront) + immutable asset caching strategy
- **Clean separation**: Bot runtime and static site are fully decoupled
- **Production‑grade infra**:
  - Dockerized services + persistent PostgreSQL volume
  - Static site in S3 fronted by CloudFront (HTTPS & caching)
  - Streamlined rollout via container + artifact pipelines
- **Great DX**: VS Code Dev Containers, bootstrap scripts, automated seeding

**Bot Backend:**
- Core runtime: Python 3.13, [discord.py](https://discordpy.readthedocs.io/)
- Market data: [yfinance](https://pypi.org/project/yfinance/)
- Data & plotting: pandas, matplotlib
- Persistence: PostgreSQL (psycopg2)
- Containerization: Docker (+ VS Code Dev Containers)
- Deployment: GitHub Actions → Docker Hub → AWS EC2

**Web Frontend:**
- Framework: React + Vite
- Deployment: GitHub Actions → AWS S3 + CloudFront CDN
- Domain: Custom domain with HTTPS via CloudFront
- Cache strategy: Immutable assets with cache-busting for HTML

See source code in [main.py](main.py), DB layer in [database_service.py](database_service.py), database bootstrap in [utils/init_db.py](utils/init_db.py), and runner scripts in [scripts/](scripts). Ticker seeding is fetched from the SEC in [utils/collect_stocks_names.py](utils/collect_stocks_names.py).

---

## Features

- Discord commands:
  - `!hello` — basic greeting
  - `!stock <ticker|company> [period]` — live price, % change, market cap + mini chart, for a given time period (default 1mo)
  - `!info <ticker|company>` — company description, sector, industry, CEO
  - `!chart <ticker|company> [period]` — historical chart (default 1mo)
  - `!news <ticker|company>` — latest news with paginated embeds
  - `!watch <ticker|company> [threshold]` — price change alerts (default 10%)
  - `!unwatch <ticker|company>` — stop alerts
  - `!unwatchall` — stop all alerts for this server
  - `!list` — list watched tickers and thresholds
  - `!metrics <ticker|company>` — key financial metrics snapshot
  - `!compare <ticker1> <ticker2> [period]` — compare two tickers
  - `!compare_sp500 <ticker> [period]` — compare a ticker vs S&P 500
  - `!help` — command reference

---

## Plans & Limits

- Free: watch up to `FREE_PLAN_MAX_WATCHED_STOCKS` tickers (default 5); access to core commands.
- Pro: higher watch limits (default 50) and premium commands:
  - `!compare`, `!compare_sp500`
  - Extended fields in `!metrics` (targets, recommendation, growth, FCF)

Environment overrides for limits:

```bash
# Optional, defaults shown
FREE_PLAN_MAX_WATCHED_STOCKS=5
PRO_PLAN_MAX_WATCHED_STOCKS=50
```

---

## Architecture

**Infrastructure:**
- **Bot Backend**: AWS EC2 + Docker + PostgreSQL
- **Web Frontend**: AWS S3 (static hosting) + CloudFront (CDN)
- **CI/CD**: GitHub Actions with dual deployment pipelines
- **Domain**: Custom domain with SSL/TLS via CloudFront

**Bot Components:**
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

## Web App (Landing Page)

This repo includes a React + Vite landing page in `aurelius-webpage/` that showcases features, pricing, and Discord chat previews. The website is completely decoupled from the bot runtime.

**Local Development:**
```bash
cd aurelius-webpage
npm install
npm run dev
```

**Production Build:**
```bash
npm run build
```

**Deployment Architecture:**
- **Hosting**: AWS S3 static website hosting
- **CDN**: CloudFront distribution for global content delivery
- **Domain**: Custom domain [aureliusbot.app](https://aureliusbot.app) with SSL/TLS
- **Cache Strategy**: 
  - HTML files: `no-cache` for immediate updates
  - Static assets: `max-age=31536000, immutable` for optimal performance
- **Deployment**: Automated via GitHub Actions on changes to `aurelius-webpage/`

## Deployment (Dual CI/CD Pipeline)

This project uses **separate GitHub Actions workflows** for independent deployment of bot and website components:

### Bot Deployment ([.github/workflows/bot-deploy.yml](.github/workflows/bot-deploy.yml))

Triggers on pushes to `main` affecting bot-related files:
- Builds and pushes Docker image to Docker Hub
- Deploys to AWS EC2 via SSH
- Handles container lifecycle management (stop/remove/pull/run)

**EC2 Prerequisites** (run once):
```bash
bash scripts/container_network.sh
bash scripts/start_bd.sh
```

### Website Deployment ([.github/workflows/website-deploy.yml](.github/workflows/website-deploy.yml))

Triggers on pushes to `main` affecting `aurelius-webpage/`:
- Builds React app with Vite
- Syncs build artifacts to AWS S3
- Invalidates CloudFront cache for immediate updates
- Implements optimized caching strategy

**Architecture Benefits:**
- **Independent scaling**: Bot and website deploy separately
- **Path-based triggers**: Only affected components redeploy
- **Optimized caching**: Static assets cached long-term, HTML files cache-busted
- **Global CDN**: CloudFront ensures low latency worldwide

---

## Portfolio Highlights

- End‑to‑end service: Discord integration, market data ingestion, charting, alerting, and news.
- Clean Python layering: Core logic in [main.py](main.py), DB access via [`database_service`](database_service.py), schema/seed in [utils/init_db.py](utils/init_db.py).
- Data seeding from the SEC’s official ticker list (no CSV maintenance).
- Production tooling: Dockerized runtime, persistent DB volume, and CI/CD to EC2.
- Dev ergonomics: VS Code Dev Container and simple scripts for running infra locally.

---

## Policies

- Privacy: see [PRIVACY_POLICY.md](PRIVACY_POLICY.md)
- Terms: see [TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md)