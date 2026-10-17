import os
import json
import click
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URLS = {
    "dev": "https://dev.api.example.com",
    "staging": "https://staging.api.example.com",
    "production": "https://api.example.com"
}

@click.command()
@click.option('--env', default='dev', type=click.Choice(['dev', 'staging', 'production']), help='Environment')
@click.option('--token', default=None, help='JWT token')
@click.option('--dry-run', is_flag=True, help='Preview request without sending')
def main(env, token, dry_run):
    token = token or os.getenv("TOKEN")
    if not token:
        click.echo("❌ Missing JWT token. Use --token or set TOKEN in .env", err=True)
        exit(1)

    url = f"{BASE_URLS[env]}/jobs/submit/single/doc"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "documentSourceIdentifier": {"documentId": "doc_123"},
        "recipientAddresses": [{"addressId": "addr_456"}],
        "jobOptions": {
            "documentClass": "businessLetter",
            "layout": "portrait",
            "mailclass": "firstClassMail",
            "paperType": "letter",
            "printOption": "color",
            "envelope": "flat"
        }
    }

    if dry_run:
        click.echo("🔧 Dry run payload:")
        click.echo(json.dumps({"url": url, "headers": headers, "json": payload}, indent=2))
        return

    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        click.echo("✅ Success:")
        click.echo(json.dumps(res.json(), indent=2))
    except requests.RequestException as err:
        click.echo(f"❌ Request failed: {err}", err=True)
        if err.response is not None:
            click.echo(err.response.text, err=True)

if __name__ == '__main__':
    main()