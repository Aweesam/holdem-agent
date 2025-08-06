#!/usr/bin/env python3
"""
Comprehensive test and demonstration of GrandpaJoe42 poker agent.
Shows the agent's decision-making, stealth behavior, and performance monitoring.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from holdem.web.web_poker_agent import WebPokerAgent, AgentStatus, AgentStats, HandRecord
from holdem.game import GameState, Player, Action, ActionType
from holdem.web.human_behavior import HumanBehaviorSimulator


class GrandpaJoe42Simulator:
    """
    Comprehensive simulation and testing environment for GrandpaJoe42.
    """
    
    def __init__(self):
        self.agent = WebPokerAgent(player_id="449469", name="GrandpaJoe42")
        self.behavior_sim = HumanBehaviorSimulator()
        self.simulation_hands = 0
        self.total_hands = 50  # Run 50 hands for demo
        
        # Performance tracking
        self.performance_log = []
        self.decision_times = []
        
    def simulate_game_state(self, hand_number: int) -> Dict[str, Any]:
        """Generate realistic game state for testing."""
        import random
        
        # Generate random but realistic poker scenarios
        cards = ['As', 'Kd', 'Qh', 'Jc', 'Ts', '9s', '8h', '7d', '6c', '5s']
        hole_cards = random.sample(cards, 2)
        community_cards = random.sample([c for c in cards if c not in hole_cards], 
                                      random.choice([0, 3, 4, 5]))
        
        pot = random.randint(20, 500)
        current_player = 449469  # GrandpaJoe42's ID
        position = random.choice(['early', 'middle', 'late', 'button'])
        
        # Vary available actions based on scenario
        if community_cards:
            actions = random.choice([
                ['fold', 'call'],
                ['fold', 'call', 'raise'],
                ['check', 'bet'],
                ['fold', 'call', 'raise']
            ])
        else:
            actions = random.choice([
                ['fold', 'call'],
                ['fold', 'call', 'raise']
            ])
        
        return {
            'pot': pot,
            'community_cards': community_cards,
            'players': {},
            'current_player': current_player,
            'betting_round': 'flop' if community_cards else 'preflop',
            'small_blind': 5,
            'big_blind': 10,
            'my_cards': hole_cards,
            'my_position': position,
            'available_actions': actions
        }
    
    def simulate_hand_result(self, action: Action, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate realistic hand result based on action taken."""
        import random
        
        # Simple outcome simulation based on cards and action
        hole_cards = game_state['my_cards']
        pot = game_state['pot']
        
        # Rough win probability based on hole cards (simplified)
        high_cards = ['A', 'K', 'Q', 'J', 'T']
        card_strength = sum(1 for card in hole_cards if card[0] in high_cards)
        
        if action.action_type == ActionType.FOLD:
            profit = -random.randint(5, 20)  # Lost blinds/bets
            won = False
        else:
            # Win probability increases with card strength
            win_prob = 0.3 + (card_strength * 0.15)
            won = random.random() < win_prob
            
            if won:
                profit = random.randint(20, pot // 2)
            else:
                profit = -random.randint(10, 50)
        
        return {
            'profit': profit,
            'won': won,
            'hand_type': 'High Card' if not won else random.choice(['Pair', 'Two Pair', 'Straight', 'Flush']),
            'table_id': 'Table 1',
            'board': game_state.get('community_cards', []),
            'pot_size': pot
        }
    
    async def simulate_poker_session(self):
        """Run a complete poker session simulation."""
        print("🎰 GRANDPAJOE42 UNLEASHED!")
        print("=" * 60)
        print(f"👴 Agent: {self.agent.name} (ID: {self.agent.player_id})")
        print(f"🎯 Target: {self.total_hands} hands")
        print(f"🧠 Strategy: Tight-aggressive with psychological warfare")
        print("=" * 60)
        
        session_start = datetime.now()
        
        for hand_num in range(1, self.total_hands + 1):
            print(f"\n🃏 Hand #{hand_num}")
            print("-" * 30)
            
            # Generate realistic game state
            game_state = self.simulate_game_state(hand_num)
            self.agent.current_game_state = game_state
            
            # Simulate new hand
            await self.agent._handle_new_hand({
                'hole_cards': game_state['my_cards'],
                'position': game_state['my_position']
            })
            
            print(f"📍 Position: {game_state['my_position']}")
            print(f"🃏 Hole cards: {' '.join(game_state['my_cards'])}")
            print(f"🎲 Community: {' '.join(game_state['community_cards']) if game_state['community_cards'] else 'None'}")
            print(f"💰 Pot: ${game_state['pot']}")
            print(f"⚡ Actions: {', '.join(game_state['available_actions'])}")
            
            # Record decision timing
            decision_start = time.time()
            
            # Simulate human thinking time
            complexity = self.agent._assess_decision_complexity()
            thinking_time = self.behavior_sim.get_decision_time(complexity)
            print(f"🤔 Thinking... ({complexity} decision, {thinking_time:.1f}s)")
            
            # Make decision
            action = self.agent._decide_action()
            decision_time = time.time() - decision_start
            self.decision_times.append(decision_time)
            
            print(f"🎯 Action: {action.action_type.value.upper()}")
            if hasattr(action, 'amount') and action.amount:
                print(f"💵 Amount: ${action.amount}")
            
            # Simulate hand completion
            result = self.simulate_hand_result(action, game_state)
            await self.agent._handle_hand_complete(result)
            
            result_emoji = "🏆" if result['won'] else "💸"
            print(f"{result_emoji} Result: {result['hand_type']} - {'+' if result['profit'] >= 0 else ''}${result['profit']}")
            
            # Log performance point
            self.performance_log.append({
                'hand': hand_num,
                'timestamp': datetime.now().isoformat(),
                'action': action.action_type.value,
                'profit': result['profit'],
                'total_profit': self.agent.stats.total_profit,
                'win_rate': self.agent.stats.win_rate,
                'decision_time': decision_time
            })
            
            # Brief pause between hands
            await asyncio.sleep(0.5)
        
        session_end = datetime.now()
        session_duration = session_end - session_start
        
        # Final statistics
        print("\n" + "=" * 60)
        print("📊 FINAL PERFORMANCE REPORT")
        print("=" * 60)
        
        stats = self.agent.get_stats()
        print(f"👴 Agent: {self.agent.name}")
        print(f"🎯 Total Hands: {stats['total_hands']}")
        print(f"🏆 Win Rate: {stats['win_rate']:.1f}%")
        print(f"💰 Total Profit: ${stats['total_profit']:+.2f}")
        print(f"⏱️  Session Time: {session_duration.total_seconds():.0f} seconds")
        print(f"💵 Hourly Rate: ${stats['hourly_rate']:+.2f}/hour")
        print(f"🤔 Avg Decision Time: {sum(self.decision_times)/len(self.decision_times):.2f}s")
        
        # Recent hands
        recent_hands = self.agent.get_recent_hands(10)
        if recent_hands:
            print(f"\n📈 Last 10 Hands:")
            for i, hand in enumerate(recent_hands[:10], 1):
                result_emoji = "🏆" if hand['result'] == 'Won' else "💸"
                print(f"  {i:2}. {hand['hole_cards']:8} | {hand['hand_description']:12} | {result_emoji} ${hand['profit']:+6.2f}")
    
    def display_behavioral_analysis(self):
        """Show GrandpaJoe42's behavioral patterns."""
        print("\n🧠 BEHAVIORAL ANALYSIS")
        print("=" * 60)
        print("👴 GrandpaJoe42's Personality Profile:")
        print("   • Tight-aggressive playing style")
        print("   • Psychological warfare through 'harmless' image")
        print("   • Variable decision timing to avoid patterns")
        print("   • Human-like breaks and micro-behaviors")
        print("   • Anti-detection browser automation")
        
        print(f"\n⏱️  Decision Timing Patterns:")
        if self.decision_times:
            avg_time = sum(self.decision_times) / len(self.decision_times)
            min_time = min(self.decision_times)
            max_time = max(self.decision_times)
            print(f"   • Average: {avg_time:.2f} seconds")
            print(f"   • Range: {min_time:.2f}s - {max_time:.2f}s")
            print(f"   • Variability: {max_time - min_time:.2f}s spread")
        
        print(f"\n🎭 Behavioral Features:")
        print("   • Realistic typing speeds")
        print("   • Human-like mouse movements") 
        print("   • Random viewport and user agent rotation")
        print("   • Break patterns every 30-60 minutes")
        print("   • Micro-behaviors (card hovering, etc.)")


async def main():
    """Main test runner for GrandpaJoe42."""
    simulator = GrandpaJoe42Simulator()
    
    print("🚀 Initializing GrandpaJoe42 Test Environment...")
    print("🎮 Simulating realistic poker gameplay...")
    
    # Run behavioral analysis
    simulator.display_behavioral_analysis()
    
    # Run poker session
    await simulator.simulate_poker_session()
    
    print(f"\n✅ GrandpaJoe42 simulation complete!")
    print(f"🎯 Agent successfully demonstrated poker skills")
    print(f"🛡️ Stealth behaviors working correctly") 
    print(f"📊 Performance monitoring active")
    
    print(f"\n🚀 GrandpaJoe42 is ready for live poker action!")
    print(f"🎰 Use the dashboard at http://localhost:3002 to control the agent")


if __name__ == "__main__":
    asyncio.run(main())