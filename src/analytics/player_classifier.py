"""
Advanced Player Classification System
Categorizes players into archetypes based on performance patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class PlayerClassifier:
    """Classifies cricket players into performance archetypes"""
    
    def __init__(self, db):
        self.db = db
    
    def classify_batsman(self, player_name: str) -> Dict:
        """
        Classify batsman into archetype
        
        Archetypes:
        - Power Hitter: SR > 145, Avg Fours+Sixes > 8
        - Anchor: SR 120-135, High consistency
        - Finisher: Most runs in death overs, SR > 140
        - Accumulator: SR 115-130, High average
        - Aggressive Opener: Position 1-2, SR > 140
        - Middle Order Stability: Position 3-5, Avg > 35
        """
        
        with self.db.get_connection() as conn:
            # Get batting stats
            query = """
                SELECT 
                    AVG(runs) as avg_runs,
                    AVG(strike_rate) as avg_sr,
                    AVG(fours + sixes) as boundaries_per_inning,
                    AVG(position) as avg_position,
                    SUM(runs) as total_runs,
                    COUNT(*) as innings,
                    SUM(CASE WHEN runs >= 50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as fifty_rate
                FROM batting_stats
                WHERE player_name = ? AND balls >= 10
            """
            
            df = pd.read_sql_query(query, conn, params=(player_name,))
            
            if len(df) == 0 or df['innings'].iloc[0] < 10:
                return {'class': 'Insufficient Data', 'confidence': 0}
            
            stats = df.iloc[0]
            avg_runs = stats['avg_runs']
            avg_sr = stats['avg_sr']
            boundaries = stats['boundaries_per_inning']
            position = stats['avg_position']
            fifty_rate = stats['fifty_rate']
            
            # Determine batting hand (simplified - based on common knowledge)
            batting_hand = self._guess_batting_hand(player_name)
            
            # Classification logic
            classification = {
                'class': '',
                'confidence': 0,
                'characteristics': [],
                'strengths': [],
                'batting_style': batting_hand,
                'stats': {
                    'average': round(avg_runs, 2),
                    'strike_rate': round(avg_sr, 2),
                    'boundaries_per_inning': round(boundaries, 2),
                    'position': round(position, 1),
                    'fifty_rate': round(fifty_rate, 1)
                }
            }
            
            # Power Hitter
            if avg_sr > 145 and boundaries > 7:
                classification['class'] = 'Power Hitter'
                classification['confidence'] = 0.85
                classification['characteristics'] = [
                    'Explosive batting',
                    'High boundary percentage',
                    'Game changer'
                ]
                classification['strengths'] = [
                    'Can accelerate quickly',
                    'Intimidates bowlers',
                    'Match-winning ability'
                ]
            
            # Finisher
            elif position > 5 and avg_sr > 140 and avg_runs > 20:
                classification['class'] = 'Finisher'
                classification['confidence'] = 0.82
                classification['characteristics'] = [
                    'Death overs specialist',
                    'High pressure performer',
                    'Lower middle order'
                ]
                classification['strengths'] = [
                    'Excellent under pressure',
                    'Can hit from ball one',
                    'Smart shot selection'
                ]
            
            # Aggressive Opener
            elif position <= 2 and avg_sr > 140:
                classification['class'] = 'Aggressive Opener'
                classification['confidence'] = 0.88
                classification['characteristics'] = [
                    'Sets tone in powerplay',
                    'Fast starter',
                    'Boundary hitter'
                ]
                classification['strengths'] = [
                    'Powerplay domination',
                    'Pressure absorber',
                    'Quick runs'
                ]
            
            # Anchor
            elif avg_sr >= 120 and avg_sr <= 135 and fifty_rate > 20:
                classification['class'] = 'Anchor'
                classification['confidence'] = 0.80
                classification['characteristics'] = [
                    'Consistent performer',
                    'Builds innings',
                    'Reliable'
                ]
                classification['strengths'] = [
                    'High consistency',
                    'Rotates strike well',
                    'Long innings'
                ]
            
            # Accumulator
            elif avg_sr >= 115 and avg_sr <= 130 and avg_runs > 30:
                classification['class'] = 'Accumulator'
                classification['confidence'] = 0.75
                classification['characteristics'] = [
                    'Steady scorer',
                    'Builds partnerships',
                    'Low risk'
                ]
                classification['strengths'] = [
                    'Dependable',
                    'Few dismissals',
                    'Good technique'
                ]
            
            # Middle Order Stabilizer
            elif position >= 3 and position <= 5 and avg_runs > 25:
                classification['class'] = 'Middle Order Stabilizer'
                classification['confidence'] = 0.78
                classification['characteristics'] = [
                    'Crisis management',
                    'Adaptable',
                    'Match awareness'
                ]
                classification['strengths'] = [
                    'Versatile batting',
                    'Anchors innings',
                    'Smart play'
                ]
            
            else:
                classification['class'] = 'All-rounder Batsman'
                classification['confidence'] = 0.65
                classification['characteristics'] = [
                    'Flexible role',
                    'Adaptable',
                    'Team player'
                ]
                classification['strengths'] = [
                    'Can bat anywhere',
                    'Multiple gears',
                    'Versatile'
                ]
            
            return classification
    
    def classify_bowler(self, player_name: str) -> Dict:
        """
        Classify bowler into archetype with bowling style
        """
        
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    AVG(economy) as avg_economy,
                    SUM(wickets) * 1.0 / COUNT(DISTINCT match_id) as wickets_per_match,
                    AVG(dots * 1.0 / (overs * 6)) as dot_ball_percentage,
                    COUNT(DISTINCT match_id) as matches,
                    SUM(wickets) as total_wickets
                FROM bowling_stats
                WHERE player_name = ? AND overs >= 2
            """
            
            df = pd.read_sql_query(query, conn, params=(player_name,))
            
            if len(df) == 0 or df['matches'].iloc[0] < 10:
                return {'class': 'Insufficient Data', 'confidence': 0}
            
            stats = df.iloc[0]
            economy = stats['avg_economy']
            wpm = stats['wickets_per_match']
            dot_pct = stats['dot_ball_percentage'] * 100
            
            # Determine bowling style (simplified)
            bowling_style = self._guess_bowling_style(player_name)
            
            classification = {
                'class': '',
                'confidence': 0,
                'characteristics': [],
                'strengths': [],
                'bowling_style': bowling_style,
                'stats': {
                    'economy': round(economy, 2),
                    'wickets_per_match': round(wpm, 2),
                    'dot_ball_percentage': round(dot_pct, 1)
                }
            }
            
            # Death Specialist
            if economy < 9 and wpm >= 0.8:
                classification['class'] = 'Death Specialist'
                classification['confidence'] = 0.85
                classification['characteristics'] = [
                    'Calm under pressure',
                    'Yorker expert',
                    'Death overs bowler'
                ]
                classification['strengths'] = [
                    'Excellent variations',
                    'Composure',
                    'Strategic bowling'
                ]
            
            # Wicket Taker
            elif wpm >= 1.3:
                classification['class'] = 'Wicket Taker'
                classification['confidence'] = 0.88
                classification['characteristics'] = [
                    'Strike bowler',
                    'Breakthrough specialist',
                    'Aggressive'
                ]
                classification['strengths'] = [
                    'Takes key wickets',
                    'Game changer',
                    'High impact'
                ]
            
            # Economy Bowler
            elif economy < 7.5 and dot_pct > 45:
                classification['class'] = 'Economy Bowler'
                classification['confidence'] = 0.82
                classification['characteristics'] = [
                    'Tight lines',
                    'Pressure builder',
                    'Difficult to score'
                ]
                classification['strengths'] = [
                    'Builds pressure',
                    'Consistent',
                    'Reliable'
                ]
            
            # Powerplay Expert
            elif wpm >= 1.0 and economy < 8:
                classification['class'] = 'Powerplay Expert'
                classification['confidence'] = 0.80
                classification['characteristics'] = [
                    'New ball specialist',
                    'Early wickets',
                    'Sets tone'
                ]
                classification['strengths'] = [
                    'Swing/seam bowling',
                    'Early breakthroughs',
                    'Restricts powerplay'
                ]
            
            else:
                classification['class'] = 'All-Phase Bowler'
                classification['confidence'] = 0.70
                classification['characteristics'] = [
                    'Versatile',
                    'Can bowl any phase',
                    'Adaptable'
                ]
                classification['strengths'] = [
                    'Flexible role',
                    'Multiple variations',
                    'Team player'
                ]
            
            return classification
    
    def _guess_batting_hand(self, player_name: str) -> str:
        """Guess batting hand based on common knowledge"""
        left_handers = {
            'S Dhawan', 'DA Warner', 'RG Sharma', 'G Gambhir', 'YK Pathan',
            'RA Jadeja', 'RV Uthappa', 'SS Iyer', 'KM Jadhav', 'SA Yadav',
            'Q de Kock', 'JC Buttler', 'KL Rahul', 'Ishan Kishan', 'T Head'
        }
        
        if player_name in left_handers:
            return 'Left-handed'
        return 'Right-handed'
    
    def _guess_bowling_style(self, player_name: str) -> str:
        """Guess bowling style based on common knowledge"""
        bowling_styles = {
            # Spinners
            'YS Chahal': 'Right-arm Leg Spin',
            'R Ashwin': 'Right-arm Off Spin',
            'Kuldeep Yadav': 'Left-arm Chinaman',
            'RA Jadeja': 'Left-arm Orthodox',
            'PP Chawla': 'Right-arm Leg Spin',
            'Imran Tahir': 'Right-arm Leg Spin',
            'RR Pant': 'Right-arm Off Spin',
            'Washington Sundar': 'Right-arm Off Spin',
            'AR Patel': 'Left-arm Orthodox',
            
            # Fast Bowlers
            'JJ Bumrah': 'Right-arm Fast',
            'B Kumar': 'Right-arm Medium Fast',
            'Mohammed Shami': 'Right-arm Fast',
            'YS Chahar': 'Right-arm Medium Fast',
            'T Natarajan': 'Left-arm Medium Fast',
            'Mohammed Siraj': 'Right-arm Fast',
            'Harshal Patel': 'Right-arm Medium',
            'AR Patel': 'Right-arm Medium',
            'S Thakur': 'Right-arm Medium Fast',
            'Mustafizur Rahman': 'Left-arm Medium Fast',
        }
        
        return bowling_styles.get(player_name, 'Right-arm Medium')
    
    def get_impact_score(self, player_name: str) -> float:
        """
        Calculate player impact score (0-100)
        Based on match-winning contributions
        """
        
        with self.db.get_connection() as conn:
            # Batting impact
            batting_query = """
                SELECT 
                    AVG(CASE 
                        WHEN runs >= 50 THEN 100
                        WHEN runs >= 30 THEN 70
                        WHEN runs >= 20 THEN 50
                        ELSE runs * 2
                    END) as batting_impact
                FROM batting_stats b
                JOIN matches m ON b.match_id = m.match_id
                WHERE b.player_name = ? AND m.winner = b.team
            """
            
            # Bowling impact
            bowling_query = """
                SELECT 
                    AVG(CASE 
                        WHEN wickets >= 3 THEN 100
                        WHEN wickets >= 2 THEN 70
                        WHEN wickets >= 1 THEN 50
                        ELSE 20
                    END) as bowling_impact
                FROM bowling_stats b
                JOIN matches m ON b.match_id = m.match_id
                WHERE b.player_name = ? AND m.winner = b.team
            """
            
            batting_impact = pd.read_sql_query(batting_query, conn, params=(player_name,))
            bowling_impact = pd.read_sql_query(bowling_query, conn, params=(player_name,))
            
            # Safe extraction with None handling
            bat_score = 0.0
            bowl_score = 0.0
            
            if len(batting_impact) > 0 and pd.notna(batting_impact['batting_impact'].iloc[0]):
                bat_score = float(batting_impact['batting_impact'].iloc[0])
            
            if len(bowling_impact) > 0 and pd.notna(bowling_impact['bowling_impact'].iloc[0]):
                bowl_score = float(bowling_impact['bowling_impact'].iloc[0])
            
            # Weighted average
            if bat_score > 0 and bowl_score > 0:
                return round((bat_score + bowl_score) / 2, 2)
            elif bat_score > 0:
                return round(bat_score, 2)
            elif bowl_score > 0:
                return round(bowl_score, 2)
            else:
                return 0.0
