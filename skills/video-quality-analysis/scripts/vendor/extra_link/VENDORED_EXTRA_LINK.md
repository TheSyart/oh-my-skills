# Vendored Extra-Link

Source: https://github.com/TheSyart/extra-link

Commit: `154fade02fd325b247d1f3c074d6a3af9267775e`

License: MIT, preserved in `LICENSE`.

Vendored files:

- `models.py`
- `request.py`
- `pharse/douyin.py`
- `pharse/kuaishou.py`
- `pharse/xhs.py`
- `pharse/bilibili.py`

Local wrapper scripts should import these files through `scripts/parse_link.py` instead of changing the vendored parser directly.
