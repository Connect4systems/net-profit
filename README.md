# Net Profit

Net Profit is a Frappe app scaffolded for Frappe Framework v15 and ERPNext v15.

## Requirements

- Frappe Framework v15
- ERPNext v15
- Python 3.10+
- Node.js 18+
- A working bench server environment

## Install On Server

From your bench directory:

```bash
cd ~/frappe-bench
bench get-app net_profit https://github.com/YOUR_ORG/net-profit.git --branch main
bench --site your-site-name install-app net_profit
bench --site your-site-name migrate
bench build
bench restart
```

For a local app folder already copied to the server:

```bash
cd ~/frappe-bench
bench get-app /path/to/net-profit
bench --site your-site-name install-app net_profit
bench --site your-site-name migrate
bench build
bench restart
```

## Development Install

```bash
cd ~/frappe-bench
bench get-app /path/to/net-profit
bench --site your-site-name install-app net_profit
bench --site your-site-name migrate
```

## Notes

The app declares Frappe and ERPNext v15 compatibility in `pyproject.toml` and requires ERPNext through `net_profit/hooks.py`.
