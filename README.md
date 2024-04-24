Ensure you have python installed on your system.

Run:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scraper.py
```

You can adjust various parameters inside the script, such as start page, total pages, and throttle.

If you want to simply scrape the entire directory, you can set `total_pages = None`.