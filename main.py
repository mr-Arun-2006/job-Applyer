import argparse
from app.config import available_providers
from app.database import init_db
from app.discovery_engine import scrape_public_job_page


def main():
    parser = argparse.ArgumentParser(description="Personal Job-Applyer")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db")
    sub.add_parser("providers")

    scrape = sub.add_parser("scrape")
    scrape.add_argument("url")

    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
        print("Database initialized.")
    elif args.command == "providers":
        for provider in available_providers():
            print(provider)
    elif args.command == "scrape":
        job = scrape_public_job_page(args.url)
        print(job["text"])


if __name__ == "__main__":
    main()
