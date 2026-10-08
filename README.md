# Serendibite Sieve

Full-colour Python 3 wine gem-sorter arcade for [ElbowOS](https://x.com/ElbowOS).

Tilt a cream sieve under a wine tent. Raspberry, cream, and chartreuse gems slide off the low end into matching chutes. Wrong chute breaks the combo.

A / D or Left / Right tilt. R restarts.

## Play

```
pip install -r requirements.txt
python3 serendibite_sieve.py --play
```

## Record a 9:16 reel

```
python3 serendibite_sieve.py
```

Writes a 1080x1920 h264 clip (15s @ 30fps) with title, score, and `x.com/ElbowOS` burned into the frames. Headless path uses `SDL_VIDEODRIVER=dummy`.

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/12voZnup0EEi-Z5MYMJFkHvPLmTXu0U3F/view
