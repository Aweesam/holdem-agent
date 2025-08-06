"""
Token management for Club WPT Gold authentication.
Handles token extraction, validation, and URL construction.
"""

import re
import time
from typing import Optional, Dict, Any
from urllib.parse import parse_qs, urlparse


class ClubWPTTokenManager:
    """Manages authentication tokens for Club WPT Gold."""
    
    def __init__(self):
        self.current_token: Optional[str] = None
        self.token_expiry: Optional[float] = None
        self.profile: str = "pg"  # Default profile
    
    def extract_token_from_url(self, url: str) -> Optional[str]:
        """Extract token from Club WPT Gold game URL."""
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if 'token' in query_params:
                token = query_params['token'][0]
                self.current_token = token
                
                # Extract profile if present
                if 'profile' in query_params:
                    self.profile = query_params['profile'][0]
                
                print(f"✅ Token extracted: {token[:20]}...")
                print(f"✅ Profile: {self.profile}")
                return token
            else:
                print("❌ No token found in URL")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting token: {e}")
            return None
    
    def construct_game_url(self, token: str, profile: str = "pg") -> str:
        """Construct the full Club WPT Gold game URL with token."""
        base_url = "https://clubwptgold.com/game/"
        return f"{base_url}?token={token}&profile={profile}"
    
    def is_token_valid(self, token: str) -> bool:
        """Check if token format appears valid."""
        if not token:
            return False
        
        # Club WPT Gold tokens appear to be 64-character hex strings
        token_pattern = re.compile(r'^[a-f0-9]{64}$')
        return bool(token_pattern.match(token))
    
    def get_current_token(self) -> Optional[str]:
        """Get currently stored token."""
        return self.current_token
    
    def set_token(self, token: str, profile: str = "pg") -> bool:
        """Set token and profile manually."""
        if self.is_token_valid(token):
            self.current_token = token
            self.profile = profile
            print(f"✅ Token set: {token[:20]}...")
            return True
        else:
            print(f"❌ Invalid token format: {token}")
            return False
    
    def get_game_url(self) -> Optional[str]:
        """Get complete game URL with current token."""
        if self.current_token:
            return self.construct_game_url(self.current_token, self.profile)
        else:
            print("❌ No token available")
            return None
    
    def clear_token(self):
        """Clear stored token."""
        self.current_token = None
        self.token_expiry = None
        print("🗑️ Token cleared")


class TokenExtractor:
    """Utility for extracting tokens from browser sessions."""
    
    @staticmethod
    def extract_from_firefox_session(browser_manager) -> Optional[str]:
        """Extract token from current Firefox session."""
        try:
            current_url = browser_manager.driver.current_url
            print(f"🔍 Current URL: {current_url}")
            
            if "clubwptgold.com" in current_url and "token=" in current_url:
                token_manager = ClubWPTTokenManager()
                return token_manager.extract_token_from_url(current_url)
            else:
                print("❌ Not on Club WPT Gold game page with token")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting from session: {e}")
            return None
    
    @staticmethod
    def wait_for_login_and_extract(browser_manager, timeout: int = 300) -> Optional[str]:
        """Wait for user to log in and extract token from URL."""
        print("⏳ Waiting for login... Please log in to Club WPT Gold in the browser window")
        print("🎯 Navigate to a poker table to get the game URL with token")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                current_url = browser_manager.driver.current_url
                
                # Check if we're on the game page with a token
                if "clubwptgold.com/game/" in current_url and "token=" in current_url:
                    print(f"✅ Found game URL: {current_url}")
                    
                    token_manager = ClubWPTTokenManager()
                    return token_manager.extract_token_from_url(current_url)
                
                # Sleep briefly before checking again
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ Error checking URL: {e}")
                time.sleep(2)
        
        print(f"⏰ Timeout after {timeout} seconds")
        return None


# Example usage and testing
if __name__ == "__main__":
    # Test token extraction
    test_url = "https://clubwptgold.com/game/?token=b0c7dc07cd9be19dfceeeb4097f91328e7fa61239f117bc31ca42ef3a43053ba&profile=pg"
    
    token_manager = ClubWPTTokenManager()
    token = token_manager.extract_token_from_url(test_url)
    
    if token:
        print(f"✅ Extracted token: {token}")
        print(f"✅ Game URL: {token_manager.get_game_url()}")
        print(f"✅ Token valid: {token_manager.is_token_valid(token)}")
    else:
        print("❌ Token extraction failed")