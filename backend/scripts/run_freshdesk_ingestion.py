#!/usr/bin/env python
"""Replay Freshdesk help articles from a JSON file through FreshdeskHelpdocsIngestion.

Examples:
    python run_freshdesk_ingestion.py                       # process every article in the default file
    python run_freshdesk_ingestion.py --limit 5             # first 5 articles
    python run_freshdesk_ingestion.py --slice 10:20         # articles 10..19
    python run_freshdesk_ingestion.py --slice :5 --limit 3  # first 5, then keep first 3
    python run_freshdesk_ingestion.py --input "JSON files/structured.json" --limit 1
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from process_agent.models.constants.event_type import EventType
from core.models.constants.source_type import SourceType
from process_agent.models.sync_event import SyncEvent
from process_agent.services.ingestion_pipelines.freshdesk_helpdocs_ingestion import (
    FreshdeskHelpdocsIngestion,
)


DEFAULT_INPUT = BASE_DIR / 'JSON files' / 'unstructured.json'


def parse_slice(spec: str) -> slice:
    parts = spec.split(':')
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f'--slice must be START:END (got {spec!r})')
    start = int(parts[0]) if parts[0] else None
    end   = int(parts[1]) if parts[1] else None
    return slice(start, end)


def parse_iso(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def build_event(article: dict) -> SyncEvent:
    source_id = str(article['id'])
    return SyncEvent.objects.create(
        source_id=source_id,
        source_type=SourceType.FRESHDESK_ARTICLE,
        source_title=article.get('title', ''),
        source_url=f'https://help.thepublive.com/support/solutions/articles/{source_id}',
        event_type=EventType.CREATED,
        source_updated_at=parse_iso(article.get('updated_at')),
        source_payload=article,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--input', type=Path, default=DEFAULT_INPUT,
        help=f'Path to article-list JSON (default: {DEFAULT_INPUT.relative_to(BASE_DIR)})',
    )
    parser.add_argument(
        '--slice', type=parse_slice, default=None,
        help='Python-style slice "START:END" (e.g. "0:10", ":5", "10:"). Applied before --limit.',
    )
    parser.add_argument(
        '--limit', type=int, default=None,
        help='Max number of articles to process (applied after --slice).',
    )
    args = parser.parse_args()

    with args.input.open() as f:
        articles = json.load(f)

    if not isinstance(articles, list):
        print(f'Expected a JSON array at top level of {args.input}, got {type(articles).__name__}', file=sys.stderr)
        return 2

    if args.slice is not None:
        articles = articles[args.slice]
    if args.limit is not None:
        articles = articles[:args.limit]

    print(f'Processing {len(articles)} article(s) from {args.input}')

    ingestion = FreshdeskHelpdocsIngestion.create()

    succeeded = 0
    failed = 0
    for article in articles:
        source_id = article.get('id', '<unknown>')
        try:
            event = build_event(article)
            ingestion.ingest(event)
            succeeded += 1
        except Exception as exc:
            failed += 1
            print(f'  [FAIL] source_id={source_id}: {exc}', file=sys.stderr)

    print(f'Done — {succeeded} succeeded, {failed} failed')
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
