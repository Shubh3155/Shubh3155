"""Activate generated cards only after all expected SVG files exist."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
for name in ('stats', 'languages', 'snake', 'snake-dark'):
    svg = ET.parse(root / 'assets' / f'{name}.svg').getroot()
    if svg.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError(f'{name} is not an SVG')

path = root / 'README.md'
text = path.read_text()
text = re.sub(r'src="https://github-readme-stats\.vercel\.app/api\?[^\"]+"',
              'src="./assets/stats.svg"', text)
text = re.sub(r'src="https://github-readme-stats\.vercel\.app/api/top-langs/\?[^\"]+"',
              'src="./assets/languages.svg"', text)
snake = '''<!-- SNAKE:START -->
<details open>
<summary><strong>A year of contributions, in motion</strong></summary>
<br />
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="./assets/snake.svg" />
  <img width="100%" src="./assets/snake.svg" alt="Animated snake traversing my GitHub contribution calendar" />
</picture>
</details>
<!-- SNAKE:END -->'''
text, count = re.subn(r'<!-- SNAKE:START -->.*?<!-- SNAKE:END -->', snake, text, flags=re.S)
if count != 1:
    raise ValueError('Expected exactly one snake placeholder in README.md')
path.write_text(text)
