"""
Advanced IPL Data Fetcher (2016-2024)
Fetches and processes comprehensive IPL match data
"""

import requests
import json
import zipfile
import io
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
from src.utils.database import IPLDatabase

print("=" * 70)
print("🏏 CricMetrics Pro - IPL Data Fetcher (2016-2024)")
print("=" * 70)

# Initialize database
db = IPLDatabase()
db.create_tables()

# Download IPL data
print("\n📥 Step 1: Downloading IPL data from Cricsheet...")
print("⏳ This may take 3-5 minutes depending on internet speed...\n")

url = "https://cricsheet.org/downloads/ipl_json.zip"

try:
    response = requests.get(url, timeout=180)
    print(f"✓ Downloaded {len(response.content) / 1024 / 1024:.1f} MB of IPL data")
except Exception as e:
    print(f"✗ Download failed: {e}")
    sys.exit(1)

# Extract and process
print("\n📊 Step 2: Processing IPL matches...")
print("⏳ Extracting and analyzing 1000+ matches...\n")

zip_file = zipfile.ZipFile(io.BytesIO(response.content))
json_files = [f for f in zip_file.namelist() if f.endswith('.json')]

# Filter for 2016 onwards
filtered_files = []
for f in json_files:
    try:
        year = int(f.split('/')[-1][:4])
        if year >= 2016:
            filtered_files.append(f)
    except:
        continue

filtered_files.sort(reverse=True)
print(f"Found {len(filtered_files)} IPL matches from 2016-2024")

processed = 0
skipped = 0
target = min(len(filtered_files), 1000)  # Process up to 1000 matches

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    for json_file in filtered_files[:target]:
        try:
            with zip_file.open(json_file) as f:
                match_data = json.load(f)
            
            info = match_data.get('info', {})
            
            # Only process IPL matches
            if 'Indian Premier League' not in str(info.get('event', {}).get('name', '')):
                skipped += 1
                continue
            
            # Extract season
            season_info = info.get('season', '2024')
            if isinstance(season_info, str):
                season = int(season_info.split('/')[0])
            else:
                season = int(season_info)
            
            # Extract match details
            match_date = info.get('dates', [datetime.now().strftime('%Y-%m-%d')])[0]
            teams = info.get('teams', [])
            if len(teams) < 2:
                skipped += 1
                continue
            
            team1, team2 = teams[0], teams[1]
            venue = info.get('venue', 'Unknown')
            city = info.get('city', 'Unknown')
            
            # Toss info
            toss = info.get('toss', {})
            toss_winner = toss.get('winner')
            toss_decision = toss.get('decision')
            
            # Outcome
            outcome = info.get('outcome', {})
            winner = outcome.get('winner')
            
            # Result details
            by = outcome.get('by', {})
            if 'runs' in by:
                result_type = 'runs'
                result_margin = by['runs']
            elif 'wickets' in by:
                result_type = 'wickets'
                result_margin = by['wickets']
            else:
                result_type = 'tie'
                result_margin = 0
            
            # Player of the match
            pom = info.get('player_of_match', [None])
            player_of_match = pom[0] if pom else None
            
            # Match type
            match_type = 'Final' if 'final' in venue.lower() or 'final' in str(info.get('event', {})).lower() else 'League'
            
            # Insert match
            cursor.execute("""
                INSERT OR IGNORE INTO matches 
                (season, match_date, venue, city, team1, team2, toss_winner, 
                 toss_decision, winner, result_type, result_margin, player_of_match, match_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (season, match_date, venue, city, team1, team2, toss_winner,
                  toss_decision, winner, result_type, result_margin, player_of_match, match_type))
            
            match_id = cursor.lastrowid
            if match_id == 0:
                skipped += 1
                continue
            
            # Process innings
            innings_num = 0
            for inning in match_data.get('innings', []):
                innings_num += 1
                team = inning.get('team')
                
                # Batting stats
                batter_stats = {}
                position = 1
                
                for over in inning.get('overs', []):
                    over_num = over.get('over', 0)
                    
                    # Determine phase
                    if over_num < 6:
                        phase = 'Powerplay'
                    elif over_num < 16:
                        phase = 'Middle'
                    else:
                        phase = 'Death'
                    
                    for delivery in over.get('deliveries', []):
                        batter = delivery.get('batter')
                        runs = delivery.get('runs', {}).get('batter', 0)
                        
                        if batter not in batter_stats:
                            batter_stats[batter] = {
                                'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0,
                                'position': position, 'dismissal': None
                            }
                            position += 1
                        
                        batter_stats[batter]['runs'] += runs
                        batter_stats[batter]['balls'] += 1
                        
                        if runs == 4:
                            batter_stats[batter]['fours'] += 1
                        elif runs == 6:
                            batter_stats[batter]['sixes'] += 1
                        
                        # Check dismissal
                        if 'wickets' in delivery:
                            for wicket in delivery['wickets']:
                                if wicket.get('player_out') == batter:
                                    batter_stats[batter]['dismissal'] = wicket.get('kind', 'out')
                
                # Insert batting stats
                for batter, stats in batter_stats.items():
                    sr = (stats['runs'] / stats['balls'] * 100) if stats['balls'] > 0 else 0
                    is_not_out = stats['dismissal'] is None
                    
                    cursor.execute("""
                        INSERT INTO batting_stats 
                        (match_id, player_name, team, innings_number, runs, balls, fours, 
                         sixes, strike_rate, position, dismissal_kind, is_not_out)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (match_id, batter, team, innings_num, stats['runs'], stats['balls'],
                          stats['fours'], stats['sixes'], sr, stats['position'],
                          stats['dismissal'], is_not_out))
                
                # Bowling stats
                bowler_stats = {}
                
                for over in inning.get('overs', []):
                    over_num = over.get('over', 0)
                    
                    # Determine phase
                    if over_num < 6:
                        phase = 'Powerplay'
                    elif over_num < 16:
                        phase = 'Middle'
                    else:
                        phase = 'Death'
                    
                    for delivery in over.get('deliveries', []):
                        bowler = delivery.get('bowler')
                        runs = delivery.get('runs', {}).get('total', 0)
                        
                        if bowler not in bowler_stats:
                            bowler_stats[bowler] = {
                                'balls': 0, 'runs': 0, 'wickets': 0,
                                'dots': 0, 'maidens': 0, 'phase': {}
                            }
                        
                        bowler_stats[bowler]['balls'] += 1
                        bowler_stats[bowler]['runs'] += runs
                        
                        if runs == 0:
                            bowler_stats[bowler]['dots'] += 1
                        
                        if 'wickets' in delivery:
                            bowler_stats[bowler]['wickets'] += len(delivery['wickets'])
                
                # Insert bowling stats
                for bowler, stats in bowler_stats.items():
                    overs = stats['balls'] / 6.0
                    economy = (stats['runs'] / overs) if overs > 0 else 0
                    
                    # Get bowling team
                    bowling_team = team2 if team == team1 else team1
                    
                    cursor.execute("""
                        INSERT INTO bowling_stats 
                        (match_id, player_name, team, innings_number, overs, runs_conceded, 
                         wickets, economy, dots)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (match_id, bowler, bowling_team, innings_num, round(overs, 1),
                          stats['runs'], stats['wickets'], round(economy, 2), stats['dots']))
            
            processed += 1
            if processed % 50 == 0:
                print(f"  ✓ Processed: {processed}/{target} matches")
                conn.commit()  # Commit every 50 matches
        
        except Exception as e:
            continue

print(f"\n{'=' * 70}")
print(f"✓ Successfully processed {processed} IPL matches!")
print(f"  Skipped: {skipped} (non-IPL or duplicates)")
print(f"✓ Database: data/ipl_analytics.db")
print(f"{'=' * 70}")

# Generate statistics
print("\n📈 Step 3: Generating statistics...")

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Count by season
    cursor.execute("""
        SELECT season, COUNT(*) as matches
        FROM matches
        GROUP BY season
        ORDER BY season DESC
    """)
    
    print("\n📊 Matches by Season:")
    for row in cursor.fetchall():
        print(f"   IPL {row[0]}: {row[1]} matches")
    
    # Top players
    cursor.execute("""
        SELECT player_name, COUNT(DISTINCT match_id) as matches, SUM(runs) as total_runs
        FROM batting_stats
        GROUP BY player_name
        ORDER BY total_runs DESC
        LIMIT 5
    """)
    
    print("\n🏆 Top 5 Run Scorers:")
    for idx, row in enumerate(cursor.fetchall(), 1):
        print(f"   {idx}. {row[0]}: {row[2]} runs in {row[1]} matches")

print(f"\n{'=' * 70}")
print("🚀 Data collection complete!")
print("=" * 70)
print("\n📌 Next Steps:")
print("   1. Run: streamlit run app.py")
print("   2. Open: http://localhost:8501")
print("   3. Explore advanced IPL analytics!\n")
