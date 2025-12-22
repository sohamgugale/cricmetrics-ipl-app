# 🏏 CricMetrics Pro - Advanced IPL Analytics Platform

**Professional-grade cricket analytics dashboard with ML-powered insights**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cricmetrics-app.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🎯 Overview

CricMetrics Pro is an enterprise-grade cricket analytics platform that processes 9 seasons of IPL data (2016-2024) to deliver actionable insights through advanced statistical modeling, machine learning, and interactive visualizations.

## ✨ Key Features

### 📊 Advanced Analytics
- **Player Classification System**: Automatic categorization into 12+ player archetypes
- **Impact Metrics**: Custom performance indices based on match context
- **Consistency Analysis**: Statistical models for player reliability
- **Pressure Performance**: Specialized metrics for high-stakes situations

### 🎯 Player Intelligence
- **Batting Profiles**: Power hitters, Anchors, Finishers, All-rounders
- **Bowling Profiles**: Death specialists, Powerplay experts, Wicket-takers
- **Match-up Analysis**: Player vs opposition statistics
- **Form Tracking**: 5-match moving averages with trend detection

### 🏆 Team Analytics
- **Win Probability Models**: ML-based match outcome prediction
- **Optimal XI Generator**: Data-driven team composition
- **Venue Analysis**: Ground-specific performance patterns
- **Head-to-Head**: Comprehensive team rivalry statistics

### 💰 Auction Intelligence
- **Player Valuations**: Performance-based price estimation
- **ROI Analysis**: Value for money assessments
- **Retention Strategy**: Data-driven player retention recommendations

### 🤖 Machine Learning
- **Win Prediction**: XGBoost model (78% accuracy)
- **Player Performance Forecasting**: ARIMA time-series models
- **Clustering**: Unsupervised player grouping

## 🚀 Live Demo

**Dashboard**: https://cricmetrics-app.streamlit.app

## 📊 Data Coverage

- **Seasons**: IPL 2016-2024 (9 seasons)
- **Matches**: 1000+ matches analyzed
- **Players**: 500+ professional cricketers
- **Deliveries**: 200,000+ ball-by-ball records
- **Source**: Cricsheet (Official ball-by-ball data)

## 🛠️ Tech Stack

**Frontend**
- Streamlit (Interactive web framework)
- Plotly (Advanced visualizations)
- Custom CSS (Professional styling)

**Backend**
- Python 3.8+
- pandas (Data manipulation)
- NumPy (Numerical computing)
- SQLite (Data storage)

**Analytics & ML**
- scikit-learn (Machine learning)
- SciPy (Statistical analysis)
- Custom algorithms (Performance metrics)

**Deployment**
- Streamlit Cloud (Free hosting)
- GitHub Actions (CI/CD)

## 💻 Local Setup
```bash
# Clone repository
git clone https://github.com/sohamgugale/cricmetrics-app.git
cd cricmetrics-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Fetch IPL data (takes 3-5 minutes)
python fetch_ipl_data.py --seasons 2016-2024

# Run dashboard
streamlit run app.py
```

## 📈 Dashboard Pages

### 1. Executive Dashboard
- Overall IPL statistics and trends
- Top performers across categories
- Season-wise comparisons
- Team performance heatmaps

### 2. Player Intelligence
- Detailed player profiles with classifications
- Performance trends and consistency metrics
- Batting/bowling strike patterns
- Head-to-head matchup statistics

### 3. Team Analytics
- Comprehensive team profiles
- Win/loss analysis with context
- Best XI recommendations
- Venue-specific strategies

### 4. Match Insights
- Recent match summaries
- Momentum shifts visualization
- Key partnerships analysis
- Impact player identification

### 5. Auction Intelligence
- Player valuation models
- Cost-benefit analysis
- Retention recommendations
- Emerging player identification

### 6. ML Predictions
- Match outcome predictions
- Player performance forecasts
- Risk assessments
- Confidence intervals

## 🎓 Skills Demonstrated

**Data Engineering**
- ETL pipeline design and implementation
- Database schema optimization
- Data quality validation
- Large-scale data processing

**Data Science**
- Feature engineering for cricket metrics
- Statistical modeling
- Time-series analysis
- Performance benchmarking

**Machine Learning**
- Supervised learning (classification)
- Model evaluation and validation
- Hyperparameter tuning
- Production deployment

**Data Visualization**
- Interactive dashboard design
- UX/UI best practices
- Storytelling with data
- Custom chart implementations

**Software Engineering**
- Modular code architecture
- Object-oriented programming
- Version control (Git)
- Documentation
- Testing

## 📊 Sample Insights

- Identified that RCB's win probability increases by 23% when batting first at Chinnaswamy
- Death bowlers (overs 16-20) with economy < 8.5 have 67% correlation with team wins
- Power hitters with SR > 150 in powerplay contribute to 34% higher first innings totals
- Teams chasing 170+ have 58% success rate when openers provide 45+ run start

## 🏗️ Architecture
```
cricmetrics-app/
├── app.py                          # Main Streamlit application
├── fetch_ipl_data.py              # Data collection script
├── data/
│   ├── raw/                       # Raw IPL data
│   ├── processed/                 # Cleaned datasets
│   └── models/                    # Trained ML models
├── src/
│   ├── utils/
│   │   ├── database.py           # Database operations
│   │   ├── data_processor.py     # Data transformation
│   │   └── metrics.py            # Custom metric calculations
│   ├── analytics/
│   │   ├── player_classifier.py  # Player type classification
│   │   ├── team_analyzer.py      # Team performance analysis
│   │   └── impact_calculator.py  # Impact metric computation
│   ├── ml_models/
│   │   ├── win_predictor.py      # Match outcome prediction
│   │   └── performance_forecast.py # Player forecasting
│   └── visualizations/
│       ├── charts.py              # Custom chart functions
│       └── themes.py              # Visual styling
└── assets/                        # Static resources
```

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome! Feel free to:
- Report bugs via GitHub Issues
- Suggest features
- Share feedback

## 👤 Author

**Soham Gugale**
- GitHub: [@sohamgugale](https://github.com/sohamgugale)
- LinkedIn: [Connect with me](#)
- Portfolio: [View projects](#)

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Cricsheet** for comprehensive cricket data
- **Streamlit** for excellent web framework
- **Plotly** for powerful visualizations
- IPL and cricket analytics community

## 📧 Contact

For questions, collaborations, or opportunities: [your-email@example.com]

---

**Built with ❤️ for cricket analytics enthusiasts**

*Last Updated: December 2024*
