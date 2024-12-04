# bot_for_run

## Features
- **Heart Rate Zones**: Calculate zones based on PANO (Peak Aerobic Power Output).
- **GPX Analysis**: Extract metrics like distance, speed, cadence, and heart rate.

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yourrepo.git
   cd yourrepo
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your bot token:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## Dependencies
- `aiogram`
- `gpxpy`
- `geopy`
- `python-dotenv`

Feel free to contribute! 🎉