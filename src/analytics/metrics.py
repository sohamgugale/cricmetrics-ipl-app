"""
Advanced Cricket Analytics Metrics
Custom performance indicators for deeper insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class AdvancedMetrics:
    """Calculate advanced cricket analytics metrics"""
    
    def __init__(self, db):
        self.db = db
    
    def consistency_index(self, player_name: str, role: str = 'batting') -> float:
        """
        Calculate consistency index (0-100)
        Lower standard deviation = higher consistency
        """
        
        with self.db.get_connection() as conn:
            if role == 'batting':
                query = """
                    SELECT runs
                    FROM batting_stats
                    WHERE player_name = ? AND balls >= 5
                    ORDER BY id DESC
                    LIMIT 20
                """
            else:
                query = """
                    SELECT economy
                    FROM bowling_stats
                    WHERE player_name = ? AND overs >= 2
                    ORDER BY id DESC
                    LIMIT 20
                """
            
            df = pd.read_sql_query(query, conn, params=(player_name,))
            
            if len(df) < 10:
                return 0.0
            
            values = df.iloc[:, 0].values
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            # Coefficient of variation (inverted and scaled)
            if mean_val > 0:
                cv = std_val / mean_val
                consistency = max(0, 100 - (cv * 100))
                return round(consistency, 2)
            
            return 0.0
    
    def pressure_performance_rating(self, player_name: str) -> Dict:
        """
        Rate performance in high-pressure situations
        - Close matches (within 20 runs)
        - Playoffs/Finals
        """
        
        with self.db.get_connection() as conn:
            # Close match performance (batting)
            close_match_query = """
                SELECT 
                    AVG(b.runs) as avg_runs,
                    AVG(b.strike_rate) as avg_sr,
                    COUNT(*) as matches
                FROM batting_stats b
                JOIN matches m ON b.match_id = m.match_id
                WHERE b.player_name = ?
                AND m.result_margin <= 20
                AND b.balls >= 10
            """
            
            # Playoff performance
            playoff_query = """
                SELECT 
                    AVG(b.runs) as playoff_avg,
                    COUNT(*) as playoff_matches
                FROM batting_stats b
                JOIN matches m ON b.match_id = m.match_id
                WHERE b.player_name = ?
                AND m.match_type IN ('Qualifier', 'Eliminator', 'Final')
                AND b.balls >= 10
            """
            
            close_df = pd.read_sql_query(close_match_query, conn, params=(player_name,))
            playoff_df = pd.read_sql_query(playoff_query, conn, params=(player_name,))
            
            # Get overall average
            overall_query = """
                SELECT AVG(runs) as overall_avg
                FROM batting_stats
                WHERE player_name = ? AND balls >= 10
            """
            overall_df = pd.read_sql_query(overall_query, conn, params=(player_name,))
            
            # Safely extract values with None handling
            close_avg = close_df['avg_runs'].iloc[0] if len(close_df) > 0 and pd.notna(close_df['avg_runs'].iloc[0]) else 0
            playoff_avg = playoff_df['playoff_avg'].iloc[0] if len(playoff_df) > 0 and pd.notna(playoff_df['playoff_avg'].iloc[0]) else 0
            overall_avg = overall_df['overall_avg'].iloc[0] if len(overall_df) > 0 and pd.notna(overall_df['overall_avg'].iloc[0]) else 1
            
            # Prevent division by zero
            if overall_avg == 0:
                overall_avg = 1
            
            # Calculate rating
            close_ratio = (close_avg / overall_avg) if close_avg > 0 else 0
            playoff_ratio = (playoff_avg / overall_avg) if playoff_avg > 0 else 0
            
            pressure_rating = ((close_ratio + playoff_ratio) / 2) * 100
            
            return {
                'rating': round(pressure_rating, 2),
                'close_match_avg': round(close_avg, 2),
                'playoff_avg': round(playoff_avg, 2),
                'overall_avg': round(overall_avg, 2),
                'performs_better_under_pressure': pressure_rating > 100
            }
    
    def strike_rotation_ability(self, player_name: str) -> float:
        """
        Measure ability to rotate strike (1s and 2s)
        Important for T20 batting
        """
        
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    SUM(runs) as total_runs,
                    SUM(fours) as fours,
                    SUM(sixes) as sixes
                FROM batting_stats
                WHERE player_name = ?
            """
            
            df = pd.read_sql_query(query, conn, params=(player_name,))
            
            if len(df) > 0 and pd.notna(df['total_runs'].iloc[0]):
                total_runs = df['total_runs'].iloc[0] or 0
                fours = df['fours'].iloc[0] or 0
                sixes = df['sixes'].iloc[0] or 0
                boundary_runs = (fours * 4) + (sixes * 6)
                
                if total_runs > 0:
                    non_boundary_pct = ((total_runs - boundary_runs) / total_runs) * 100
                    return round(non_boundary_pct, 2)
            
            return 0.0
    
    def matchup_analysis(self, batsman: str, bowler: str) -> Dict:
        """
        Analyze head-to-head batsman vs bowler
        """
        
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    b.player_name as batsman,
                    bo.player_name as bowler,
                    AVG(b.runs) as avg_runs,
                    AVG(b.strike_rate) as avg_sr,
                    COUNT(*) as encounters
                FROM batting_stats b
                JOIN bowling_stats bo ON b.match_id = bo.match_id
                WHERE b.player_name = ? AND bo.player_name = ?
                AND b.balls >= 5
            """
            
            df = pd.read_sql_query(query, conn, params=(batsman, bowler))
            
            if len(df) > 0 and df['encounters'].iloc[0] > 0:
                return {
                    'encounters': int(df['encounters'].iloc[0]),
                    'batsman_avg': round(df['avg_runs'].iloc[0], 2),
                    'strike_rate': round(df['avg_sr'].iloc[0], 2),
                    'advantage': 'Batsman' if df['avg_sr'].iloc[0] > 140 else 'Bowler'
                }
            
            return {'encounters': 0, 'note': 'Insufficient data'}
    
    def phase_wise_performance(self, player_name: str, role: str = 'batting') -> Dict:
        """
        Performance breakdown by match phase
        Powerplay (1-6), Middle (7-15), Death (16-20)
        """
        
        with self.db.get_connection() as conn:
            if role == 'batting':
                powerplay = """
                    SELECT AVG(runs) as avg, AVG(strike_rate) as sr
                    FROM batting_stats
                    WHERE player_name = ? AND position <= 2
                """
                
                middle = """
                    SELECT AVG(runs) as avg, AVG(strike_rate) as sr
                    FROM batting_stats
                    WHERE player_name = ? AND position BETWEEN 3 AND 5
                """
                
                death = """
                    SELECT AVG(runs) as avg, AVG(strike_rate) as sr
                    FROM batting_stats
                    WHERE player_name = ? AND position >= 6
                """
                
                pp_df = pd.read_sql_query(powerplay, conn, params=(player_name,))
                mid_df = pd.read_sql_query(middle, conn, params=(player_name,))
                death_df = pd.read_sql_query(death, conn, params=(player_name,))
                
                return {
                    'powerplay': {
                        'avg': round(pp_df['avg'].iloc[0], 2) if len(pp_df) > 0 and pd.notna(pp_df['avg'].iloc[0]) else 0,
                        'sr': round(pp_df['sr'].iloc[0], 2) if len(pp_df) > 0 and pd.notna(pp_df['sr'].iloc[0]) else 0
                    },
                    'middle': {
                        'avg': round(mid_df['avg'].iloc[0], 2) if len(mid_df) > 0 and pd.notna(mid_df['avg'].iloc[0]) else 0,
                        'sr': round(mid_df['sr'].iloc[0], 2) if len(mid_df) > 0 and pd.notna(mid_df['sr'].iloc[0]) else 0
                    },
                    'death': {
                        'avg': round(death_df['avg'].iloc[0], 2) if len(death_df) > 0 and pd.notna(death_df['avg'].iloc[0]) else 0,
                        'sr': round(death_df['sr'].iloc[0], 2) if len(death_df) > 0 and pd.notna(death_df['sr'].iloc[0]) else 0
                    }
                }
            
            return {}
