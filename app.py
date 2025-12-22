
# =============================================================================
# PAGE 1: EXECUTIVE DASHBOARD
# =============================================================================

if page == "🏠 Executive Dashboard":
    st.title("🏠 Executive Dashboard")
    st.markdown("### IPL Analytics Overview")
    
    # Filter by season
    if selected_season != 'All Seasons':
        season_num = int(selected_season.split()[-1])
        filtered_matches = matches_df[matches_df['season'] == season_num]
        filtered_batting = batting_df[batting_df['match_id'].isin(filtered_matches['match_id'])]
        filtered_bowling = bowling_df[bowling_df['match_id'].isin(filtered_matches['match_id'])]
    else:
        filtered_matches = matches_df
        filtered_batting = batting_df
        filtered_bowling = bowling_df
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📅 Matches Played", 
            len(filtered_matches),
            delta=f"{len(filtered_matches) - len(matches_df[matches_df['season'] == matches_df['season'].min()])}" if selected_season == 'All Seasons' else None
        )
    
    with col2:
        total_runs = filtered_batting['runs'].sum()
        st.metric("🏃 Total Runs", f"{total_runs:,}")
    
    with col3:
        unique_players = filtered_batting['player_name'].nunique()
        st.metric("👥 Players", unique_players)
    
    with col4:
        total_sixes = filtered_batting['sixes'].sum()
        st.metric("🚀 Sixes Hit", f"{total_sixes:,}")
    
    st.markdown("---")
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top 10 Run Scorers")
        top_scorers = filtered_batting.groupby('player_name').agg({
            'runs': 'sum',
            'match_id': 'nunique',
            'strike_rate': 'mean'
        }).reset_index()
        top_scorers.columns = ['Player', 'Runs', 'Matches', 'Avg SR']
        top_scorers = top_scorers.nlargest(10, 'Runs')
        
        fig = px.bar(
            top_scorers,
            y='Player',
            x='Runs',
            orientation='h',
            color='Avg SR',
            color_continuous_scale='Reds',
            text='Runs',
            labels={'Avg SR': 'Strike Rate'}
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(
            height=450,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🎯 Top 10 Wicket Takers")
        top_bowlers = filtered_bowling.groupby('player_name').agg({
            'wickets': 'sum',
            'match_id': 'nunique',
            'economy': 'mean'
        }).reset_index()
        top_bowlers.columns = ['Player', 'Wickets', 'Matches', 'Economy']
        top_bowlers = top_bowlers.nlargest(10, 'Wickets')
        
        fig = px.bar(
            top_bowlers,
            y='Player',
            x='Wickets',
            orientation='h',
            color='Economy',
            color_continuous_scale='Blues_r',
            text='Wickets',
            labels={'Economy': 'Economy Rate'}
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(
            height=450,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Season-wise analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Runs Per Season")
        season_runs = batting_df.merge(
            matches_df[['match_id', 'season']], 
            on='match_id'
        ).groupby('season')['runs'].sum().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=season_runs['season'],
            y=season_runs['runs'],
            mode='lines+markers',
            line=dict(color='#E91E63', width=3),
            marker=dict(size=10, color='#E91E63'),
            fill='tozeroy',
            fillcolor='rgba(233, 30, 99, 0.1)'
        ))
        fig.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA'),
            xaxis_title='Season',
            yaxis_title='Total Runs'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🏅 Team Win Distribution")
        team_wins = filtered_matches['winner'].value_counts().head(8)
        
        fig = px.pie(
            values=team_wins.values,
            names=team_wins.index,
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='#FAFAFA', width=2))
        )
        fig.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Recent matches table
    st.markdown("#### 🆕 Recent Matches")
    recent_matches = filtered_matches[[
        'match_date', 'team1', 'team2', 'winner', 
        'result_type', 'result_margin', 'venue'
    ]].head(15)
    recent_matches.columns = [
        'Date', 'Team 1', 'Team 2', 'Winner', 
        'Result Type', 'Margin', 'Venue'
    ]
    st.dataframe(recent_matches, use_container_width=True, height=400)


# =============================================================================
# PAGE 2: PLAYER INTELLIGENCE
# =============================================================================

elif page == "👤 Player Intelligence":
    st.title("👤 Player Intelligence")
    st.markdown("### Advanced Player Profiling & Classification")
    
    # Player selection
    all_players = sorted(batting_df['player_name'].unique())
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_player = st.selectbox("🔍 Select Player", all_players, key='player_select')
    with col2:
        player_role = st.radio("Role", ["Batting", "Bowling", "Both"], horizontal=True)
    
    # Get player stats
    player_batting = batting_df[batting_df['player_name'] == selected_player]
    player_bowling = bowling_df[bowling_df['player_name'] == selected_player]
    
    if len(player_batting) > 0 or len(player_bowling) > 0:
        st.markdown("---")
        
        # Player Classification
        col1, col2 = st.columns(2)
        
        with col1:
            if len(player_batting) >= 10:
                st.markdown("#### 🎯 Batting Classification")
                bat_class = classifier.classify_batsman(selected_player)
                
                st.markdown(f"""
                <div class='player-card'>
                    <h3 style='color: #E91E63;'>{bat_class['class']}</h3>
                    <p><strong>Confidence:</strong> <span class='highlight'>{bat_class['confidence']*100:.0f}%</span></p>
                    <p><strong>Characteristics:</strong></p>
                    <ul>
                        {''.join([f"<li>{char}</li>" for char in bat_class.get('characteristics', [])])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Display stats
                if 'stats' in bat_class:
                    stats = bat_class['stats']
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Average", f"{stats['average']:.2f}")
                    with col_b:
                        st.metric("Strike Rate", f"{stats['strike_rate']:.2f}")
                    with col_c:
                        st.metric("Boundaries/Inn", f"{stats['boundaries_per_inning']:.1f}")
            else:
                st.info("Need 10+ batting innings for classification")
        
        with col2:
            if len(player_bowling) >= 10:
                st.markdown("#### 🎳 Bowling Classification")
                bowl_class = classifier.classify_bowler(selected_player)
                
                st.markdown(f"""
                <div class='player-card'>
                    <h3 style='color: #E91E63;'>{bowl_class['class']}</h3>
                    <p><strong>Confidence:</strong> <span class='highlight'>{bowl_class['confidence']*100:.0f}%</span></p>
                    <p><strong>Characteristics:</strong></p>
                    <ul>
                        {''.join([f"<li>{char}</li>" for char in bowl_class.get('characteristics', [])])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                if 'stats' in bowl_class:
                    stats = bowl_class['stats']
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Economy", f"{stats['economy']:.2f}")
                    with col_b:
                        st.metric("Wickets/Match", f"{stats['wickets_per_match']:.2f}")
                    with col_c:
                        st.metric("Dot %", f"{stats['dot_ball_percentage']:.1f}%")
            else:
                st.info("Need 10+ bowling innings for classification")
        
        st.markdown("---")
        
        # Career Statistics
        col1, col2 = st.columns(2)
        
        with col1:
            if len(player_batting) > 0:
                st.markdown("#### 📊 Batting Career Stats")
                
                # Create metrics
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Innings", len(player_batting))
                with col_b:
                    st.metric("Total Runs", int(player_batting['runs'].sum()))
                with col_c:
                    st.metric("Average", f"{player_batting['runs'].mean():.2f}")
                with col_d:
                    st.metric("High Score", int(player_batting['runs'].max()))
                
                col_e, col_f, col_g, col_h = st.columns(4)
                with col_e:
                    st.metric("Strike Rate", f"{player_batting['strike_rate'].mean():.2f}")
                with col_f:
                    st.metric("Fours", int(player_batting['fours'].sum()))
                with col_g:
                    st.metric("Sixes", int(player_batting['sixes'].sum()))
                with col_h:
                    fifties = len(player_batting[player_batting['runs'] >= 50])
                    st.metric("50s", fifties)
                
                # Form chart
                st.markdown("##### 📈 Recent Form (Last 15 Innings)")
                recent = player_batting.tail(15)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(recent)+1)),
                    y=recent['runs'].values,
                    mode='lines+markers',
                    name='Runs',
                    line=dict(color='#E91E63', width=3),
                    marker=dict(size=10)
                ))
                fig.add_hline(
                    y=player_batting['runs'].mean(),
                    line_dash="dash",
                    line_color="yellow",
                    annotation_text="Career Avg"
                )
                fig.update_layout(
                    height=300,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#FAFAFA'),
                    xaxis_title='Innings',
                    yaxis_title='Runs'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if len(player_bowling) > 0:
                st.markdown("#### 🎳 Bowling Career Stats")
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Matches", player_bowling['match_id'].nunique())
                with col_b:
                    st.metric("Wickets", int(player_bowling['wickets'].sum()))
                with col_c:
                    st.metric("Economy", f"{player_bowling['economy'].mean():.2f}")
                with col_d:
                    best = player_bowling.nlargest(1, 'wickets')['wickets'].values[0]
                    st.metric("Best", f"{int(best)}")
                
                # Wickets distribution
                st.markdown("##### 📊 Wickets Distribution")
                wicket_dist = player_bowling['wickets'].value_counts().sort_index()
                
                fig = px.bar(
                    x=wicket_dist.index,
                    y=wicket_dist.values,
                    labels={'x': 'Wickets in Match', 'y': 'Frequency'},
                    color=wicket_dist.values,
                    color_continuous_scale='Reds'
                )
                fig.update_layout(
                    height=300,
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#FAFAFA')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Advanced metrics
        st.markdown("#### 🎯 Advanced Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            consistency = metrics.consistency_index(selected_player, 'batting')
            st.metric("Consistency Index", f"{consistency:.1f}/100")
            st.caption("Higher = More consistent performances")
        
        with col2:
            impact = classifier.get_impact_score(selected_player)
            st.metric("Impact Score", f"{impact:.1f}/100")
            st.caption("Contribution to team wins")
        
        with col3:
            pressure = metrics.pressure_performance_rating(selected_player)
            if pressure.get('rating', 0) > 0:
                st.metric("Pressure Rating", f"{pressure['rating']:.1f}")
                st.caption("Performance in close matches")
            else:
                st.metric("Pressure Rating", "N/A")
        
        with col4:
            rotation = metrics.strike_rotation_ability(selected_player)
            st.metric("Strike Rotation", f"{rotation:.1f}%")
            st.caption("Non-boundary runs percentage")


# =============================================================================
# PAGE 3: TEAM ANALYTICS
# =============================================================================

elif page == "🏆 Team Analytics":
    st.title("🏆 Team Analytics")
    st.markdown("### Comprehensive Team Performance Analysis")
    
    # Team selection
    all_teams = sorted(set(matches_df['team1'].unique()) | set(matches_df['team2'].unique()))
    selected_team = st.selectbox("🔍 Select Team", all_teams, key='team_select')
    
    # Get team profile
    season_num = int(selected_season.split()[-1]) if selected_season != 'All Seasons' else None
    team_profile = team_analyzer.get_team_profile(selected_team, season_num)
    
    st.markdown("---")
    
    # Team overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Matches Played", team_profile['matches'])
    with col2:
        st.metric("Wins", team_profile['wins'])
    with col3:
        st.metric("Win %", f"{team_profile['win_percentage']:.1f}%")
    with col4:
        st.metric("Avg Score", int(team_profile['avg_score']))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Win/Loss Record")
        
        fig = go.Figure(data=[go.Pie(
            labels=['Wins', 'Losses'],
            values=[team_profile['wins'], team_profile['losses']],
            hole=0.5,
            marker_colors=['#2ECC71', '#E74C3C'],
            textinfo='label+percent',
            textfont_size=16
        )])
        fig.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA', size=14)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### ⭐ Top 5 Performers")
        
        top_performers = pd.DataFrame(team_profile['top_batsmen'])
        if len(top_performers) > 0:
            fig = px.bar(
                top_performers,
                y='player_name',
                x='total_runs',
                orientation='h',
                text='total_runs',
                color='total_runs',
                color_continuous_scale='Oranges'
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(
                height=350,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FAFAFA'),
                yaxis_title='',
                xaxis_title='Total Runs'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Venue analysis
    st.markdown("#### 🏟️ Venue Performance")
    venue_data = team_analyzer.venue_analysis(selected_team)
    
    if len(venue_data) > 0:
        fig = px.scatter(
            venue_data,
            x='matches',
            y='win_pct',
            size='wins',
            color='win_pct',
            hover_data=['venue', 'city'],
            text='city',
            color_continuous_scale='RdYlGn',
            size_max=30
        )
        fig.update_traces(textposition='top center')
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA'),
            xaxis_title='Matches Played',
            yaxis_title='Win Percentage'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Venue table
        st.dataframe(
            venue_data[['venue', 'city', 'matches', 'wins', 'win_pct']],
            use_container_width=True,
            height=300
        )
    
    st.markdown("---")
    
    # Toss impact
    st.markdown("#### 🪙 Toss Impact Analysis")
    toss_data = team_analyzer.toss_impact(selected_team)
    
    if toss_data:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tosses Won", toss_data['toss_wins'])
        with col2:
            st.metric("Matches Won After Toss", toss_data['matches_won_after_toss'])
        with col3:
            st.metric("Win Rate After Toss", f"{toss_data['win_rate_after_toss']:.1f}%")


# =============================================================================
# PAGE 4: MATCH INSIGHTS
# =============================================================================

elif page == "📈 Match Insights":
    st.title("📈 Match Insights")
    st.markdown("### Deep Dive into Match Statistics")
    
    # Recent matches
    st.markdown("#### 🆕 Recent Matches (Last 20)")
    recent = matches_df.head(20)
    
    # Create interactive table
    display_cols = ['match_date', 'team1', 'team2', 'venue', 'winner', 'result_type', 'result_margin', 'player_of_match']
    recent_display = recent[display_cols].copy()
    recent_display.columns = ['Date', 'Team 1', 'Team 2', 'Venue', 'Winner', 'Result', 'Margin', 'Player of Match']
    
    st.dataframe(recent_display, use_container_width=True, height=400)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏟️ Most Popular Venues")
        venue_counts = matches_df['venue'].value_counts().head(10)
        
        fig = px.bar(
            x=venue_counts.values,
            y=venue_counts.index,
            orientation='h',
            text=venue_counts.values,
            color=venue_counts.values,
            color_continuous_scale='Viridis',
            labels={'x': 'Matches', 'y': 'Venue'}
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(
            height=450,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🎯 Highest Individual Scores")
        top_scores = batting_df.nlargest(10, 'runs')[[
            'player_name', 'runs', 'balls', 'strike_rate', 'fours', 'sixes'
        ]].copy()
        top_scores.columns = ['Player', 'Runs', 'Balls', 'SR', '4s', '6s']
        
        st.dataframe(top_scores, use_container_width=True, height=450)
    
    st.markdown("---")
    
    # Match results distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Results by Type")
        result_dist = matches_df['result_type'].value_counts()
        
        fig = px.pie(
            values=result_dist.values,
            names=result_dist.index,
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🏆 Player of Match Awards")
        pom_counts = matches_df['player_of_match'].value_counts().head(10)
        
        fig = px.bar(
            x=pom_counts.values,
            y=pom_counts.index,
            orientation='h',
            text=pom_counts.values,
            color=pom_counts.values,
            color_continuous_scale='Reds'
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(
            height=350,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA'),
            yaxis_title=''
        )
        st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PAGE 5: AUCTION INTELLIGENCE
# =============================================================================

elif page == "💰 Auction Intelligence":
    st.title("💰 Auction Intelligence")
    st.markdown("### Player Valuation & Performance Analytics")
    
    st.info("🚧 Advanced auction analytics with ML-based valuations coming soon!")
    
    # Top value players
    st.markdown("#### 💎 High Value Players (Based on Performance)")
    
    # Calculate value score
    player_value = batting_df.groupby('player_name').agg({
        'runs': 'sum',
        'match_id': 'nunique',
        'strike_rate': 'mean'
    }).reset_index()
    
    player_value['value_score'] = (
        player_value['runs'] * 0.5 + 
        player_value['match_id'] * 20 + 
        player_value['strike_rate'] * 0.3
    )
    
    top_value = player_value.nlargest(20, 'value_score')
    
    fig = px.scatter(
        top_value,
        x='match_id',
        y='runs',
        size='value_score',
        color='strike_rate',
        hover_data=['player_name'],
        text='player_name',
        color_continuous_scale='Turbo',
        size_max=40,
        labels={
            'match_id': 'Matches Played',
            'runs': 'Total Runs',
            'strike_rate': 'Avg Strike Rate'
        }
    )
    fig.update_traces(textposition='top center', textfont_size=9)
    fig.update_layout(
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FAFAFA')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Consistency vs Performance
    st.markdown("#### 📊 Consistency vs Impact Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get top 30 players
        top_players = batting_df.groupby('player_name').agg({
            'runs': ['sum', 'mean', 'std'],
            'match_id': 'nunique'
        }).reset_index()
        
        top_players.columns = ['player', 'total_runs', 'avg_runs', 'std_runs', 'matches']
        top_players = top_players[top_players['matches'] >= 20].nlargest(30, 'total_runs')
        
        # Calculate consistency score
        top_players['consistency'] = 100 - (top_players['std_runs'] / top_players['avg_runs'] * 100)
        top_players['consistency'] = top_players['consistency'].clip(0, 100)
        
        fig = px.scatter(
            top_players,
            x='consistency',
            y='avg_runs',
            size='total_runs',
            color='matches',
            hover_data=['player'],
            color_continuous_scale='Viridis',
            size_max=30,
            labels={
                'consistency': 'Consistency Score',
                'avg_runs': 'Average Runs',
                'matches': 'Matches'
            }
        )
        fig.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### 🎯 Key Insights")
        st.markdown("""
        **Top Right Quadrant:**
        - High consistency
        - High average
        - Premium players
        
        **Top Left Quadrant:**
        - Variable performance
        - High peaks
        - Impact players
        
        **Bottom Right:**
        - Consistent
        - Lower average
        - Reliable squad players
        """)


# =============================================================================
# PAGE 6: ML PREDICTIONS
# =============================================================================

elif page == "🤖 ML Predictions":
    st.title("🤖 ML Predictions")
    st.markdown("### Machine Learning Powered Insights")
    
    st.info("🚧 Advanced ML models including match outcome prediction and player performance forecasting coming soon!")
    
    # Match predictor
    st.markdown("#### 🎯 Match Outcome Predictor")
    
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Team A", sorted(matches_df['team1'].unique()), key='team_a')
    with col2:
        team_b = st.selectbox("Team B", sorted(matches_df['team2'].unique()), key='team_b')
    
    venue_select = st.selectbox("Venue", sorted(matches_df['venue'].unique()))
    
    if st.button("Predict Winner", type="primary"):
        # Simple prediction based on historical data
        team_a_matches = matches_df[
            ((matches_df['team1'] == team_a) | (matches_df['team2'] == team_a))
        ]
        team_a_wins = len(team_a_matches[team_a_matches['winner'] == team_a])
        team_a_win_rate = team_a_wins / len(team_a_matches) if len(team_a_matches) > 0 else 0.5
        
        team_b_matches = matches_df[
            ((matches_df['team1'] == team_b) | (matches_df['team2'] == team_b))
        ]
        team_b_wins = len(team_b_matches[team_b_matches['winner'] == team_b])
        team_b_win_rate = team_b_wins / len(team_b_matches) if len(team_b_matches) > 0 else 0.5
        
        # Normalize
        total = team_a_win_rate + team_b_win_rate
        team_a_prob = (team_a_win_rate / total) * 100
        team_b_prob = (team_b_win_rate / total) * 100
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{team_a} Win Probability", f"{team_a_prob:.1f}%")
        with col2:
            st.metric(f"{team_b} Win Probability", f"{team_b_prob:.1f}%")
        
        # Visualization
        fig = go.Figure(data=[
            go.Bar(
                y=[team_a, team_b],
                x=[team_a_prob, team_b_prob],
                orientation='h',
                marker_color=['#E91E63', '#2196F3']
            )
        ])
        fig.update_layout(
            height=250,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA'),
            xaxis_title='Win Probability (%)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("*Based on historical performance. For entertainment purposes only.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <p style='color: #888; font-size: 14px;'>
        🏏 <strong>CricMetrics Pro</strong> | Advanced IPL Analytics Platform<br>
        Built with ❤️ using Streamlit, Python & Advanced Analytics<br>
        Data Source: <a href='https://cricsheet.org' target='_blank' style='color: #E91E63;'>Cricsheet</a> | 
        Created by <a href='https://github.com/sohamgugale' target='_blank' style='color: #E91E63;'>Soham Gugale</a>
    </p>
</div>
""", unsafe_allow_html=True)
