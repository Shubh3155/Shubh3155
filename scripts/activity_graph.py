"""Render a repository-hosted graph from GitHub's contribution calendar."""
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


def render(days):
    days = sorted(days, key=lambda day: day['date'])[-31:]
    if not days or any(not isinstance(d['contributionCount'], int) or d['contributionCount'] < 0 for d in days):
        raise ValueError('Expected dated, nonnegative contribution counts')
    width, height = 1000, 300
    left, right, top, bottom = 60, 970, 76, 238
    peak = max(4, max(d['contributionCount'] for d in days))
    points = [(left + i * (right-left) / max(1, len(days)-1), bottom - d['contributionCount'] * (bottom-top) / peak) for i, d in enumerate(days)]
    line = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
    total = sum(d['contributionCount'] for d in days)
    label = f"{days[0]['date']} to {days[-1]['date']} · {total} contributions"
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
           '<title id="title">Recent GitHub contribution activity</title>',
           f'<desc id="desc">{escape(label)}. Daily contribution counts from GitHub.</desc>',
           '<rect width="1000" height="300" rx="16" fill="#0d1117"/>',
           '<g font-family="Segoe UI, sans-serif">',
           '<text x="30" y="33" fill="#a78bfa" font-size="20" font-weight="600">Recent contribution activity</text>',
           f'<text x="30" y="56" fill="#8b949e" font-size="12">{escape(label)}</text>']
    for i in range(5):
        y = bottom - i * (bottom-top)/4
        svg += [f'<path d="M{left} {y}H{right}" stroke="#21262d"/>',
                f'<text x="45" y="{y+4}" text-anchor="end" fill="#8b949e" font-size="11">{peak*i/4:g}</text>']
    svg += [f'<polygon points="{points[0][0]},{bottom} {line} {points[-1][0]},{bottom}" fill="#67e8f9" opacity=".08"/>',
            f'<polyline points="{line}" fill="none" stroke="#67e8f9" stroke-width="2.5" stroke-linejoin="round"/>']
    for i, ((x, y), day) in enumerate(zip(points, days)):
        svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="#c4b5fd"><title>{escape(day["date"])}: {day["contributionCount"]} contributions</title></circle>')
        if i % 5 == 0 or i == len(days)-1:
            svg.append(f'<text x="{x:.2f}" y="261" text-anchor="middle" fill="#8b949e" font-size="11">{escape(day["date"][5:])}</text>')
    svg += ['<text x="970" y="286" text-anchor="end" fill="#8b949e" font-size="11">GitHub contribution calendar · refreshed daily</text>', '</g></svg>']
    return '\n'.join(svg)


def main():
    now = datetime.now(timezone.utc)
    query = '''query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar { weeks { contributionDays { date contributionCount } } }
        }
      }
    }'''
    payload = {'query': query, 'variables': {'login': 'Shubh3155', 'from': (now-timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat(), 'to': now.isoformat()}}
    request = Request('https://api.github.com/graphql', data=json.dumps(payload).encode(), headers={'Authorization': f'Bearer {os.environ["GITHUB_TOKEN"]}', 'Content-Type': 'application/json', 'User-Agent': 'profile-visuals'})
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError('GitHub contribution calendar query failed')
    calendar = result['data']['user']['contributionsCollection']['contributionCalendar']
    days = [day for week in calendar['weeks'] for day in week['contributionDays']]
    output = Path(__file__).resolve().parents[1] / 'assets/activity.svg'
    output.write_text(render(days))


if __name__ == '__main__':
    main()
