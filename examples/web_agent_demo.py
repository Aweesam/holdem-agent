#!/usr/bin/env python3
"""
Demo of web-based stealth poker agent.
"""

import os
import time
from holdem.web import BrowserManager, HumanBehaviorSimulator


def demo_stealth_behavior():
    """Demonstrate stealth behavior patterns."""
    print("=== Stealth Behavior Demo ===")
    
    behavior_sim = HumanBehaviorSimulator()
    
    # Test decision timing
    print("Decision timing examples:")
    for complexity in ["simple", "normal", "complex"]:
        decision_time = behavior_sim.get_decision_time(complexity)
        print(f"  {complexity}: {decision_time:.2f} seconds")
    
    print("\nMicro-behavior examples:")
    for _ in range(5):
        behavior = behavior_sim.add_random_micro_behavior()
        if behavior:
            print(f"  Would perform: {behavior}")
    
    print(f"\nBreak recommendation: {behavior_sim.should_take_break()}")
    if behavior_sim.should_take_break():
        duration = behavior_sim.get_break_duration()
        print(f"Break duration: {duration:.1f} seconds")


def demo_browser_automation():
    """Demonstrate browser automation (requires Chrome driver)."""
    print("\n=== Browser Automation Demo ===")
    
    try:
        with BrowserManager(headless=False) as browser:
            print("Browser initialized successfully")
            
            # Navigate to a test site
            test_url = "https://example.com"
            print(f"Navigating to {test_url}")
            
            if browser.navigate_to_game(test_url):
                print("Navigation successful")
                
                # Simulate human-like page interaction
                browser.simulate_reading_time(200)
                browser.scroll_randomly()
                
                print("Demo completed successfully")
            else:
                print("Navigation failed")
                
    except Exception as e:
        print(f"Browser demo failed: {e}")
        print("Note: This requires Chrome and chromedriver to be installed")


def demo_poker_site_structure():
    """Demo the planned structure for poker site interaction."""
    print("\n=== Poker Site Integration Structure ===")
    
    game_url = "https://friendsimulatedholdem.com/game/?token=&profile=pg"
    print(f"Target site: {game_url}")
    
    print("\nPlanned interaction flow:")
    print("1. Initialize stealth browser")
    print("2. Navigate to poker site with human-like timing")
    print("3. Parse game state from DOM")
    print("4. Make poker decisions using our engine")
    print("5. Execute actions with human-like behavior")
    print("6. Monitor for changes and adapt")
    
    print("\nStealth features implemented:")
    print("- Randomized user agents and viewports")
    print("- Human-like mouse movements and click variations")
    print("- Realistic typing speeds and decision timing")
    print("- Break patterns and micro-behaviors")
    print("- Anti-detection browser settings")


if __name__ == "__main__":
    demo_stealth_behavior()
    demo_browser_automation()
    demo_poker_site_structure()