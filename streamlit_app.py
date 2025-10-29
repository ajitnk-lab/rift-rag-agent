import streamlit as st
import requests
import json
from typing import Dict, List, Any

# Page config
st.set_page_config(
    page_title="🎮 Rift RAG - League of Legends AI Assistant",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mock data based on actual KB content
MOCK_DATA = {
    "players": ["CoreJJ", "Ruler", "Hide on bush"],
    "champions": ["Jinx", "Xayah", "Jax", "Aphelios", "AurelionSol", "Orianna", "Lissandra", "Leblanc"],
    "matches": [
        {"id": "NA1_5386028998", "player": "CoreJJ", "champion": "Jinx", "kda": "10/12/18", "result": "Defeat", "mode": "ARAM", "duration": "14", "gold": "12165", "cs": "61"},
        {"id": "NA1_5386008300", "player": "CoreJJ", "champion": "Xayah", "kda": "8/6/12", "result": "Victory", "mode": "ARAM", "duration": "16", "gold": "11500", "cs": "45"},
        {"id": "NA1_5385991931", "player": "CoreJJ", "champion": "Jax", "kda": "19/9/15", "result": "Victory", "mode": "ARAM", "duration": "15", "gold": "13008", "cs": "27"},
        {"id": "KR_7883724608", "player": "Ruler", "champion": "Aphelios", "kda": "12/8/14", "result": "Defeat", "mode": "CLASSIC", "duration": "28", "gold": "14200", "cs": "180"},
        {"id": "KR_7883708763", "player": "Ruler", "champion": "AurelionSol", "kda": "10/8/16", "result": "Defeat", "mode": "ARAM", "duration": "14", "gold": "10242", "cs": "18"},
        {"id": "KR_7883679974", "player": "Ruler", "champion": "Orianna", "kda": "13/7/20", "result": "Victory", "mode": "ARAM", "duration": "19", "gold": "15780", "cs": "100"}
    ]
}

# API Configuration
API_ENDPOINT = st.secrets.get("API_ENDPOINT", "")

def call_bedrock_agent(query: str) -> str:
    """Call Bedrock Agent via API Gateway with proper error handling"""
    if not API_ENDPOINT:
        return "⚠️ API endpoint not configured. Using mock response for demo."
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        payload = {"query": query}
        
        response = requests.post(
            f"{API_ENDPOINT}/query",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'No response received')
        else:
            return f"❌ API Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ Connection Error: {str(e)}"

def create_champion_card(champion: str, matches: List[Dict]) -> None:
    """Create interactive champion performance card"""
    champion_matches = [m for m in matches if m['champion'] == champion]
    
    if not champion_matches:
        return
    
    wins = len([m for m in champion_matches if m['result'] == 'Victory'])
    total = len(champion_matches)
    win_rate = (wins / total * 100) if total > 0 else 0
    
    avg_kda = calculate_avg_kda([m['kda'] for m in champion_matches])
    
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏆 Win Rate", f"{win_rate:.1f}%")
        with col2:
            st.metric("🎯 Avg KDA", f"{avg_kda:.1f}")
        with col3:
            st.metric("📊 Games", total)
        with col4:
            if st.button(f"Analyze {champion}", key=f"analyze_{champion}"):
                query = f"Analyze {champion} performance across all matches"
                with st.spinner("🤖 Analyzing..."):
                    response = call_bedrock_agent(query)
                st.code(response, language=None)

def calculate_avg_kda(kda_list: List[str]) -> float:
    """Calculate average KDA from string format 'K/D/A'"""
    total_kda = 0
    for kda_str in kda_list:
        try:
            k, d, a = map(int, kda_str.split('/'))
            kda = (k + a) / max(d, 1)  # Avoid division by zero
            total_kda += kda
        except:
            continue
    return total_kda / len(kda_list) if kda_list else 0

def create_player_comparison():
    """Create player vs player comparison tool"""
    st.subheader("👥 Player Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        player1 = st.selectbox("Player 1", MOCK_DATA["players"], key="player1")
    with col2:
        player2 = st.selectbox("Player 2", MOCK_DATA["players"], key="player2")
    
    if player1 != player2:
        if st.button("🔍 Compare Players"):
            query = f"Compare {player1} vs {player2} performance, strengths and weaknesses"
            with st.spinner("🤖 Analyzing player comparison..."):
                response = call_bedrock_agent(query)
            st.code(response, language=None)

def create_quick_insights():
    """Create one-click insight generators"""
    st.subheader("⚡ Quick Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏆 Best Performers"):
            query = "Who are the best performing players and what makes them successful?"
            with st.spinner("🤖 Generating insights..."):
                response = call_bedrock_agent(query)
            st.success(response)
    
    with col2:
        if st.button("📈 Meta Analysis"):
            query = "What are the current meta trends and champion priorities?"
            with st.spinner("🤖 Analyzing meta..."):
                response = call_bedrock_agent(query)
            st.success(response)
    
    with col3:
        if st.button("🎯 Performance Tips"):
            query = "What are key performance improvement tips based on professional data?"
            with st.spinner("🤖 Generating tips..."):
                response = call_bedrock_agent(query)
            st.success(response)

def create_interactive_filters():
    """Create real-time data filtering interface"""
    st.subheader("🔍 Interactive Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        selected_player = st.selectbox("Filter by Player", ["All"] + MOCK_DATA["players"])
    with col2:
        selected_mode = st.selectbox("Game Mode", ["All", "ARAM", "CLASSIC"])
    with col3:
        selected_result = st.selectbox("Result", ["All", "Victory", "Defeat"])
    with col4:
        selected_champion = st.selectbox("Champion", ["All"] + MOCK_DATA["champions"])
    
    # Filter matches based on selections
    filtered_matches = MOCK_DATA["matches"]
    
    if selected_player != "All":
        filtered_matches = [m for m in filtered_matches if m["player"] == selected_player]
    if selected_mode != "All":
        filtered_matches = [m for m in filtered_matches if m["mode"] == selected_mode]
    if selected_result != "All":
        filtered_matches = [m for m in filtered_matches if m["result"] == selected_result]
    if selected_champion != "All":
        filtered_matches = [m for m in filtered_matches if m["champion"] == selected_champion]
    
    # Display filtered results
    if filtered_matches:
        st.write(f"📊 Found {len(filtered_matches)} matches:")
        
        # Create a simple table display
        for match in filtered_matches:
            with st.expander(f"{match['player']} - {match['champion']} ({match['result']})"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**KDA:** {match['kda']}")
                with col2:
                    st.write(f"**Mode:** {match['mode']}")
                with col3:
                    st.write(f"**Duration:** {match['duration']}m")
                with col4:
                    st.write(f"**Gold:** {match['gold']}")
        
        if st.button("🤖 Analyze Filtered Data"):
            filter_desc = f"player: {selected_player}, mode: {selected_mode}, result: {selected_result}, champion: {selected_champion}"
            query = f"Analyze the filtered matches with {filter_desc}. What patterns do you see?"
            with st.spinner("🤖 Analyzing filtered data..."):
                response = call_bedrock_agent(query)
            st.code(response, language=None)
    else:
        st.warning("No matches found with current filters.")

# Main App
def main():
    st.title("🎮 Rift RAG - League of Legends AI Assistant")
    st.markdown("*Powered by AWS Bedrock Agent & S3 Vectors*")
    
    # Sidebar with overall stats
    with st.sidebar:
        st.header("📊 Overview")
        st.metric("👥 Players", len(MOCK_DATA["players"]))
        st.metric("🎯 Champions", len(MOCK_DATA["champions"]))
        st.metric("🎮 Total Matches", len(MOCK_DATA["matches"]))
        
        # Win rate calculation
        wins = len([m for m in MOCK_DATA["matches"] if m["result"] == "Victory"])
        total_matches = len(MOCK_DATA["matches"])
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
        st.metric("🏆 Overall Win Rate", f"{win_rate:.1f}%")
        
        st.markdown("---")
        st.markdown("**Available Players:**")
        for player in MOCK_DATA["players"]:
            st.write(f"• {player}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Champion Cards", "👥 Player Comparison", "⚡ Quick Insights", "🔍 Filters", "💬 Chat"])
    
    with tab1:
        st.header("🎯 Champion Performance Cards")
        st.markdown("Click on any champion to see detailed performance analysis")
        
        # Create champion cards in single column for better readability
        for champion in MOCK_DATA["champions"]:
            with st.expander(f"🎮 {champion}", expanded=False):
                create_champion_card(champion, MOCK_DATA["matches"])
    
    with tab2:
        create_player_comparison()
    
    with tab3:
        create_quick_insights()
    
    with tab4:
        create_interactive_filters()
    
    with tab5:
        st.header("💬 Chat with Rift AI")
        st.markdown("Ask any question about League of Legends performance data")
        
        # Chat interface
        user_query = st.text_input("Ask me anything about the match data:", placeholder="e.g., 'What champions perform best in ARAM?'")
        
        if st.button("🚀 Ask Rift AI") and user_query:
            with st.spinner("🤖 Thinking..."):
                response = call_bedrock_agent(user_query)
            
            # Create a wide container for better layout
            with st.container():
                st.markdown("### 🤖 Rift AI Response")
                st.markdown("---")
                # Use code block for wide display
                st.code(response, language=None)
        
        # Sample questions
        st.markdown("### 💡 Sample Questions:")
        sample_questions = [
            "What champions did CoreJJ perform best with?",
            "Compare ARAM vs CLASSIC game performance", 
            "Which player has the highest KDA?",
            "What are the key factors for victory?",
            "Show me the longest duration matches"
        ]
        
        for question in sample_questions:
            if st.button(f"💭 {question}", key=f"sample_{question}"):
                with st.spinner("🤖 Processing..."):
                    response = call_bedrock_agent(question)
                
                # Create a wide container for better layout
                with st.container():
                    st.markdown("### 🤖 Rift AI Response")
                    st.markdown("---")
                    # Use code block for wide display
                    st.code(response, language=None)

if __name__ == "__main__":
    main()
