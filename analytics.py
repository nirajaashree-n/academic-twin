import streamlit as st
import sqlite3
from collections import defaultdict
import plotly.graph_objects as go

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.title("📊 Analytics")

# Fetch data from database
conn = sqlite3.connect("academic_twin.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT topic, COUNT(*) as count, SUM(score_delta) as total_score_delta
    FROM interactions
    GROUP BY topic
    ORDER BY count DESC
""")

data = cursor.fetchall()
conn.close()

if not data:
    st.info("No analytics data yet. Start chatting to generate data!")
else:
    topics = [row[0] for row in data]
    counts = [row[1] for row in data]
    score_deltas = [row[2] for row in data]
    
    # Bar chart: Messages by topic
    fig = go.Figure(data=[
        go.Bar(x=topics, y=counts, marker_color='#2196f3', text=counts, textposition='auto')
    ])
    fig.update_layout(
        title="Messages by Topic",
        xaxis_title="Topic",
        yaxis_title="Count",
        height=500,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Bar chart: Score delta by topic
    fig2 = go.Figure(data=[
        go.Bar(x=topics, y=score_deltas, marker_color='#4caf50', text=[f"{s:.1f}" for s in score_deltas], textposition='auto')
    ])
    fig2.update_layout(
        title="Total Score Change by Topic",
        xaxis_title="Topic",
        yaxis_title="Score Delta",
        height=500,
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Summary stats
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Messages", sum(counts))
    col2.metric("Topics Covered", len(topics))
    col3.metric("Total Score Change", f"{sum(score_deltas):.1f}")
