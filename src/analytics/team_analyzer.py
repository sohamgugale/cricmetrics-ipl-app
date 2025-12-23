"""
Team Performance Analysis Module
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class TeamAnalyzer:
    """Comprehensive team analytics"""
    
    def __init__(self, db):
        self.db = db
    
    def get_team_profile(self, team_name: str, season: int = None) -> Dict:
        """Get comprehensive team profile"""
        
        with self.db.get_connection() as conn:
            season_filter = f"AND m.season = {season}" if season else ""
            
            # Win/Loss record
            record_query = f"""
                SELECT 
                    COUNT(*) as matches,
                    SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN winner IS NULL THEN 1 ELSE 0 END) as no_results
                FROM matches m
                WHERE (team1 = ? OR team2 = ?) {season_filter}
            """
            
            record_df = pd.read_sql_query(
                record_query, conn, 
                params=(team_name, team_name, team_name)
            )
            
            matches = int(record_df['matches'].iloc[0])
            wins = int(record_df['wins'].iloc[0])
            losses = matches - wins - int(record_df['no_results'].iloc[0])
            win_pct = (wins / matches * 100) if matches > 0 else 0
            
            # Batting stats
            batting_query = f"""
                SELECT 
                    AVG(total_runs) as avg_score,
                    MAX(total_runs) as highest_score
                FROM (
                    SELECT match_id, SUM(runs) as total_runs
                    FROM batting_stats
                    WHERE team = ?
                    GROUP BY match_id
                )
            """
            
            batting_df = pd.read_sql_query(batting_query, conn, params=(team_name,))
            
            # Top performers
            top_batsmen_query = f"""
                SELECT player_name, SUM(runs) as total_runs, COUNT(*) as innings
                FROM batting_stats b
                JOIN matches m ON b.match_id = m.match_id
                WHERE b.team = ? {season_filter}
                GROUP BY player_name
                ORDER BY total_runs DESC
                LIMIT 5
            """
            
            top_batsmen = pd.read_sql_query(top_batsmen_query, conn, params=(team_name,))
            
            return {
                'matches': matches,
                'wins': wins,
                'losses': losses,
                'win_percentage': round(win_pct, 2),
                'avg_score': round(batting_df['avg_score'].iloc[0], 2) if len(batting_df) > 0 else 0,
                'highest_score': int(batting_df['highest_score'].iloc[0]) if len(batting_df) > 0 else 0,
                'top_batsmen': top_batsmen.to_dict('records')
            }
    
    def venue_analysis(self, team_name: str) -> pd.DataFrame:
        """Analyze team performance by venue"""
        
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    venue,
                    city,
                    COUNT(*) as matches,
                    SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) as wins,
                    ROUND(SUM(CASE WHEN winner = ? THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) as win_pct
                FROM matches
                WHERE (team1 = ? OR team2 = ?)
                GROUP BY venue, city
                HAVING matches >= 3
                ORDER BY win_pct DESC
            """
            
            return pd.read_sql_query(
                query, conn,
                params=(team_name, team_name, team_name, team_name)
            )
    
    def toss_impact(self, team_name: str) -> Dict:
        """Analyze impact of winning toss"""
        
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    COUNT(*) as toss_wins,
                    SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) as match_wins
                FROM matches
                WHERE toss_winner = ?
            """
            
            df = pd.read_sql_query(query, conn, params=(team_name, team_name))
            
            if len(df) > 0:
                toss_wins = int(df['toss_wins'].iloc[0])
                match_wins = int(df['match_wins'].iloc[0])
                win_rate = (match_wins / toss_wins * 100) if toss_wins > 0 else 0
                
                return {
                    'toss_wins': toss_wins,
                    'matches_won_after_toss': match_wins,
                    'win_rate_after_toss': round(win_rate, 2)
                }
            
            return {}
