"""
Browser management for stealth web interaction.
"""

import time
import random
from typing import Optional, Dict, Any, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .human_behavior import HumanBehaviorSimulator


class BrowserManager:
    """Manages browser instance with stealth capabilities."""
    
    def __init__(self, headless: bool = False, user_data_dir: Optional[str] = None):
        self.driver: Optional[webdriver.Chrome] = None
        self.behavior_sim = HumanBehaviorSimulator()
        self.headless = headless
        self.user_data_dir = user_data_dir
        self._setup_driver()
    
    def _setup_driver(self) -> None:
        """Initialize Chrome driver with stealth settings."""
        options = Options()
        
        # Stealth settings to avoid detection
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Randomize user agent
        user_agents = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Viewport randomization
        viewports = [(1366, 768), (1920, 1080), (1440, 900), (1536, 864)]
        viewport = random.choice(viewports)
        options.add_argument(f"--window-size={viewport[0]},{viewport[1]}")
        
        if self.headless:
            options.add_argument("--headless")
        
        if self.user_data_dir:
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # Additional privacy/stealth options
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Faster loading
        options.add_argument("--disable-javascript")  # Can be enabled per-site if needed
        
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # Execute script to remove automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize browser: {e}")
    
    def navigate_to_game(self, url: str) -> bool:
        """Navigate to the poker game URL with human-like behavior."""
        try:
            # Simulate human navigation pattern
            self.driver.get("https://google.com")  # Visit a common site first
            time.sleep(random.uniform(1, 3))
            
            # Navigate to actual game
            self.driver.get(url)
            
            # Wait for page load with human-like patience
            wait_time = random.uniform(3, 8)
            time.sleep(wait_time)
            
            return True
            
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False
    
    def human_click(self, element, offset_variation: int = 5) -> bool:
        """Perform human-like click with slight position variation."""
        try:
            # Get element location and size
            location = element.location
            size = element.size
            
            # Calculate click position with variation
            x = location['x'] + size['width'] // 2
            y = location['y'] + size['height'] // 2
            
            x, y = self.behavior_sim.vary_click_position(x, y, offset_variation)
            
            # Simulate mouse movement delay
            time.sleep(self.behavior_sim.get_mouse_movement_delay())
            
            # Perform click
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.pause(random.uniform(0.1, 0.3))
            actions.click()
            actions.perform()
            
            return True
            
        except Exception as e:
            print(f"Click failed: {e}")
            return False
    
    def human_type(self, element, text: str) -> bool:
        """Type text with human-like timing."""
        try:
            element.clear()
            
            # Calculate typing delay
            total_delay = self.behavior_sim.get_typing_delay(len(text))
            char_delay = total_delay / len(text) if text else 0
            
            for char in text:
                element.send_keys(char)
                time.sleep(char_delay + random.uniform(-0.02, 0.02))
            
            return True
            
        except Exception as e:
            print(f"Typing failed: {e}")
            return False
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for element with human-like patience."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            
            # Add small delay to simulate human recognition time
            time.sleep(random.uniform(0.2, 0.8))
            
            return element
            
        except TimeoutException:
            return None
    
    def scroll_randomly(self) -> None:
        """Perform random small scrolls to appear human."""
        if random.random() < 0.1:  # 10% chance
            scroll_amount = random.randint(-100, 100)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.5, 1.5))
    
    def simulate_reading_time(self, content_length: int = 100) -> None:
        """Simulate time spent reading content."""
        # Assume average reading speed of 200-300 words per minute
        words = content_length / 5  # Rough word count
        reading_speed = random.uniform(200, 300)  # words per minute
        reading_time = (words / reading_speed) * 60  # seconds
        
        # Cap reading time and add variation
        reading_time = min(reading_time, 10)  # Max 10 seconds
        reading_time = max(reading_time, 0.5)  # Min 0.5 seconds
        
        time.sleep(reading_time + random.uniform(-0.2, 0.5))
    
    def take_human_break(self) -> None:
        """Take a break if human behavior suggests it."""
        if self.behavior_sim.should_take_break():
            break_duration = self.behavior_sim.get_break_duration()
            print(f"Taking human-like break for {break_duration:.1f} seconds")
            time.sleep(break_duration)
    
    def close(self) -> None:
        """Close browser safely."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()