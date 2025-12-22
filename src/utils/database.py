"""
Professional Database Manager for CricMetrics Pro
Handles IPL data storage with advanced querying
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict
import pandas as pd


class IPLDatabase:
    """Advanced IPL Database Manager"""
    
    def __init__(self, db_path: str = "data/ipl_analytics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def create_tables(self):
        """Create comprehensive database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Matches table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    season INTEGER NOT NULL,
                    match_number INTEGER,
                    match_date DATE,
                    venue TEXT,
                    city TEXT,
                    team1 TEXT NOT NULL,
                    team2 TEXT NOT NULL,
                    toss_winner TEXT,
                    toss_decision TEXT,
                    winner TEXT,
                    result_type TEXT,
                    result_margin INTEGER,
                    player_of_match TEXT,
                    umpire1 TEXT,
                    umpire2 TEXT,
                    match_type TEXT DEFAULT 'League',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Players table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT UNIQUE NOT NULL,
                    country TEXT,
                    player_type TEXT,
                    batting_style TEXT,
                    bowling_style TEXT,
                    primary_role TEXT,
                    is_overseas BOOLEAN DEFAULT 0
                )
            """)
            
            # Batting performances
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS batting_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    player_name TEXT NOT NULL,
                    team TEXT NOT NULL,
                    innings_number INTEGER,
                    runs INTEGER NOT NULL,
                    balls INTEGER NOT NULL,
                    fours INTEGER DEFAULT 0,
                    sixes INTEGER DEFAULT 0,
                    strike_rate REAL,
                    position INTEGER,
                    dismissal_kind TEXT,
                    is_not_out BOOLEAN DEFAULT 0,
                    phase TEXT,
                    FOREIGN KEY (match_id) REFERENCES matches(match_id)
                )
            """)
            
            # Bowling performances
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bowling_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    player_name TEXT NOT NULL,
                    team TEXT NOT NULL,
                    innings_number INTEGER,
                    overs REAL NOT NULL,
                    maidens INTEGER DEFAULT 0,
                    runs_conceded INTEGER NOT NULL,
                    wickets INTEGER NOT NULL,
                    economy REAL,
                    dots INTEGER DEFAULT 0,
                    phase TEXT,
                    FOREIGN KEY (match_id) REFERENCES matches(match_id)
                )
            """)
            
            # Player classifications
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_classifications (
                    player_name TEXT PRIMARY KEY,
                    batting_class TEXT,
                    bowling_class TEXT,
                    overall_role TEXT,
                    consistency_score REAL,
                    impact_score REAL,
                    pressure_rating REAL,
                    powerplay_specialist BOOLEAN DEFAULT 0,
                    death_specialist BOOLEAN DEFAULT 0,
                    finisher BOOLEAN DEFAULT 0
                )
            """)
            
            # Team statistics cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_stats_cache (
                    team_name TEXT,
                    season INTEGER,
                    matches_played INTEGER,
                    matches_won INTEGER,
                    win_percentage REAL,
                    avg_score INTEGER,
                    highest_score INTEGER,
                    lowest_score INTEGER,
                    PRIMARY KEY (team_name, season)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_season ON matches(season)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_batting_player ON batting_stats(player_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bowling_player ON bowling_stats(player_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_batting_match ON batting_stats(match_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bowling_match ON bowling_stats(match_id)")
            
            print("✓ Database schema created successfully")
    
    def get_player_stats(self, player_name: str, season: Optional[int] = None) -> Dict:
        """Get comprehensive player statistics"""
        with self.get_connection() as conn:
            season_filter = f"AND m.season = {season}" if season else ""
            
            batting_query = f"""
                SELECT 
                    COUNT(DISTINCT b.match_id) as matches,
                    COUNT(b.id) as innings,
                    SUM(b.runs) as total_runs,
                    AVG(b.runs) as avg_runs,
                    MAX(b.runs) as highest_score,
                    AVG(b.strike_rate) as avg_sr,
                    SUM(b.fours) as total_fours,
                    SUM(b.sixes) as total_sixes,
                    SUM(CASE WHEN b.runs >= 50 THEN 1 ELSE 0 END) as fifties,
                    SUM(CASE WHEN b.runs >= 100 THEN 1 ELSE 0 END) as hundreds
                FROM batting_stats b
                JOIN matches m ON b.match_id = m.match_id
                WHERE b.player_name = ? {season_filter}
            """
            
            bowling_query = f"""
                SELECT 
                    COUNT(DISTINCT b.match_id) as matches,
                    SUM(b.overs) as total_overs,
                    SUM(b.wickets) as total_wickets,
                    AVG(b.economy) as avg_economy,
                    SUM(b.runs_conceded) as runs_conceded,
                    SUM(CASE WHEN b.wickets >= 3 THEN 1 ELSE 0 END) as three_wickets,
                    SUM(CASE WHEN b.wickets >= 4 THEN 1 ELSE 0 END) as four_wickets
                FROM bowling_stats b
                JOIN matches m ON b.match_id = m.match_id
                WHERE b.player_name = ? {season_filter}
            """
            
            batting_df = pd.read_sql_query(batting_query, conn, params=(player_name,))
            bowling_df = pd.read_sql_query(bowling_query, conn, params=(player_name,))
            
            return {
                'batting': batting_df.to_dict('records')[0] if len(batting_df) > 0 else {},
                'bowling': bowling_df.to_dict('records')[0] if len(bowling_df) > 0 else {}
            }
    
    def get_team_performance(self, team_name: str, season: Optional[int] = None) -> pd.DataFrame:
        """Get team performance metrics"""
        with self.get_connection() as conn:
            season_filter = f"AND season = {season}" if season else ""
            
            query = f"""
                SELECT 
                    season,
                    COUNT(*) as matches,
                    SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN winner != ? AND winner IS NOT NULL THEN 1 ELSE 0 END) as losses,
                    ROUND(SUM(CASE WHEN winner = ? THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) as win_pct
                FROM matches
                WHERE (team1 = ? OR team2 = ?) {season_filter}
                GROUP BY season
                ORDER BY season DESC
            """
            
            return pd.read_sql_query(
                query, conn, 
                params=(team_name, team_name, team_name, team_name, team_name)
            )


# Initialize database
def init_database():
    db = IPLDatabase()
    db.create_tables()
    return db
