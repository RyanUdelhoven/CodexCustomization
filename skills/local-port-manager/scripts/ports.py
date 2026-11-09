#!/usr/bin/env python3
"""Persistent, transaction-safe local TCP/UDP port assignments (macOS/Unix)."""
import argparse
import contextlib
import datetime
import errno
import json
from pathlib import Path
import socket
import sqlite3
import sys


def available(port, protocol):
    kind = socket.SOCK_STREAM if protocol == 'tcp' else socket.SOCK_DGRAM
    with contextlib.ExitStack() as stack:
        for family, address in ((socket.AF_INET, '0.0.0.0'), (socket.AF_INET6, '::')):
            try:
                sock = stack.enter_context(socket.socket(family, kind))
                if family == socket.AF_INET6:
                    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                sock.bind((address, port))
            except OSError as exc:
                if family == socket.AF_INET6 and exc.errno in (errno.EAFNOSUPPORT, errno.EPROTONOSUPPORT, errno.EADDRNOTAVAIL):
                    continue
                if exc.errno in (errno.EADDRINUSE, errno.EACCES):
                    return False
                raise
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=Path.home()/'.codex/local-ports/ports.sqlite3')
    subs = parser.add_subparsers(dest='action', required=True)
    subs.add_parser('list')
    subs.add_parser('check')
    for name in ('allocate', 'release'):
        sub = subs.add_parser(name)
        sub.add_argument('--project', required=True, type=Path)
        sub.add_argument('--service', required=True)
        sub.add_argument('--protocol', choices=('tcp', 'udp'), default='tcp')
        if name == 'allocate':
            sub.add_argument('--port', type=int, help='Import or request this exact host port')
            sub.add_argument('--minimum', type=int, default=3000)
            sub.add_argument('--maximum', type=int, default=9999)
            sub.add_argument('--adopt-occupied', action='store_true', help='Only after verifying the listener belongs to this project')
    args = parser.parse_args()
    if args.action == 'allocate':
        if not 1024 <= args.minimum <= args.maximum <= 65535:
            parser.error('range must satisfy 1024 <= minimum <= maximum <= 65535')
        if args.port is not None and not 1024 <= args.port <= 65535:
            parser.error('port must be between 1024 and 65535')
        if args.adopt_occupied and args.port is None:
            parser.error('--adopt-occupied requires --port')
    registry = args.registry.expanduser().resolve()
    # Inspection does not create a registry or require a write permission.
    if args.action in ('list', 'check') and not registry.exists():
        print('[]')
        return
    if args.action in ('list', 'check'):
        connection = sqlite3.connect(registry.as_uri()+'?mode=ro', uri=True, timeout=15)
    else:
        registry.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(registry, timeout=15, isolation_level=None)
    connection.row_factory = sqlite3.Row
    try:
        if args.action in ('allocate', 'release'):
            connection.execute('BEGIN IMMEDIATE')
            connection.execute('''CREATE TABLE IF NOT EXISTS assignments (
                project TEXT NOT NULL, service TEXT NOT NULL, protocol TEXT NOT NULL,
                port INTEGER NOT NULL, created TEXT NOT NULL,
                PRIMARY KEY(project, service, protocol), UNIQUE(port, protocol))''')
        if args.action in ('list', 'check'):
            rows = [dict(row) for row in connection.execute('SELECT * FROM assignments ORDER BY project, service, protocol')]
            if args.action == 'check':
                for row in rows:
                    row['bind_available'] = available(row['port'], row['protocol'])
            result = rows
        else:
            project = str(args.project.expanduser().resolve(strict=args.action == 'allocate'))
            if args.action == 'allocate' and not Path(project).is_dir():
                raise ValueError('project must be an existing directory')
            if not args.service.strip():
                raise ValueError('service must not be empty')
            key = (project, args.service, args.protocol)
            existing = connection.execute('SELECT * FROM assignments WHERE project=? AND service=? AND protocol=?', key).fetchone()
            if args.action == 'release':
                connection.execute('DELETE FROM assignments WHERE project=? AND service=? AND protocol=?', key)
                result = {'released': dict(existing) if existing else None}
            elif existing:
                if args.port is not None and args.port != existing['port']:
                    raise ValueError('service already assigned; explicitly release before changing its port')
                result = dict(existing)
                result.update(reused=True, bind_available=available(existing['port'], args.protocol))
            else:
                candidates = [args.port] if args.port is not None else range(args.minimum, args.maximum+1)
                chosen = None
                for port in candidates:
                    if connection.execute('SELECT 1 FROM assignments WHERE port=? AND protocol=?', (port, args.protocol)).fetchone():
                        continue
                    if available(port, args.protocol) or args.adopt_occupied:
                        chosen = port
                        break
                if chosen is None:
                    raise ValueError('no eligible port: requested port is registered/occupied or range is exhausted')
                created = datetime.datetime.now(datetime.timezone.utc).isoformat()
                connection.execute('INSERT INTO assignments VALUES (?,?,?,?,?)', (*key, chosen, created))
                result = dict(project=project, service=args.service, protocol=args.protocol, port=chosen, created=created, reused=False, bind_available=available(chosen, args.protocol))
            connection.commit()
        print(json.dumps(result, indent=2))
    finally:
        connection.close()


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
