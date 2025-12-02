"""
Chrome Debug Mode Driver (VBA Original Method)
"""
import os
import time
import logging
import subprocess
import platform
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pathlib import Path

logger = logging.getLogger(__name__)


class ChromeDriver:
    """Chrome Debug Mode Driver (VBA Original Method)"""
    
    def __init__(self, driver_path=None, headless: bool = False, 
                 use_debug_mode: bool = True, debug_port: int = 9222, 
                 profile_path: str = None):
        """
        Initialize
        
        Args:
            driver_path: ChromeDriver path (auto-detect if None)
            headless: Headless mode flag
            use_debug_mode: Debug mode flag (VBA original method, recommended)
            debug_port: Debug port number (default 9222)
            profile_path: Chrome profile path (uses ~/ChromeTEMP if None)
        """
        self.driver_path = driver_path or self._find_chromedriver()
        self.headless = headless
        self.use_debug_mode = use_debug_mode
        self.debug_port = debug_port
        self.profile_path = profile_path or os.path.expanduser("~/ChromeTEMP")
        self.chrome_pid = None
        
        logger.info(f"ChromeDriver initialized: headless={headless}, debug_mode={use_debug_mode}")
        if use_debug_mode:
            logger.info(f"Profile path: {self.profile_path}")
    
    def _find_chrome_path(self) -> Optional[str]:
        """Find Chrome executable path"""
        system = platform.system()
        
        if system == "Windows":
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]
        elif system == "Darwin":  # macOS
            possible_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ]
        else:  # Linux
            possible_paths = [
                "/usr/bin/google-chrome",
                "/usr/local/bin/google-chrome",
                "/usr/bin/chromium-browser",
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Chrome executable found: {path}")
                return path
        
        logger.error("Chrome executable not found.")
        return None
    
    def _find_chromedriver(self) -> str:
        """Auto-detect ChromeDriver path"""
        # Check drivers folder in project
        project_root = Path(__file__).parent.parent
        driver_path = project_root / "drivers" / "chromedriver.exe"
        
        if driver_path.exists():
            logger.info(f"ChromeDriver found: {driver_path}")
            return str(driver_path)
        
        # Check environment variable
        env_path = os.getenv("CHROME_DRIVER_PATH")
        if env_path and Path(env_path).exists():
            return env_path
        
        logger.warning("ChromeDriver path not found. Using system PATH.")
        return "chromedriver"
    
    def start_chrome_debug_mode(self) -> Optional[int]:
        """
        Start Chrome in debug mode (VBA original method)
        
        Returns:
            Chrome process PID, None on failure
        """
        try:
            chrome_path = self._find_chrome_path()
            if not chrome_path:
                logger.error("Chrome executable not found.")
                return None
            
            # Create profile directory
            os.makedirs(self.profile_path, exist_ok=True)
            logger.info(f"Profile directory ready: {self.profile_path}")
            
            # Chrome debug mode command
            cmd = [
                chrome_path,
                f"--remote-debugging-port={self.debug_port}",
                f"--user-data-dir={self.profile_path}",
                "--disable-sync",                      # Disable sync
                "--no-first-run",                      # Skip first run page
                "--no-default-browser-check",          # Skip default browser check
            ]
            
            logger.info(f"Starting Chrome debug mode: port {self.debug_port}")
            
            # Start process in background
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            self.chrome_pid = process.pid
            logger.info(f"Chrome process started: PID={self.chrome_pid}")
            
            # Wait for Chrome to be ready
            time.sleep(3)
            
            return self.chrome_pid
            
        except Exception as e:
            logger.error(f"Failed to start Chrome debug mode: {e}")
            return None
    
    def create_driver(self) -> webdriver.Chrome:
        """Create Chrome driver"""
        try:
            # Start Chrome first if using debug mode
            if self.use_debug_mode:
                logger.info("[WRENCH] Starting Chrome in debug mode (VBA original method)")
                pid = self.start_chrome_debug_mode()
                if not pid:
                    logger.error("Debug mode start failed, switching to normal mode")
                    self.use_debug_mode = False
            
            # Create Chrome options
            options = self._create_chrome_options()
            
            # Create driver
            if self.use_debug_mode:
                # Connect to debug port
                logger.info(f"Connecting to debug port {self.debug_port}...")
                driver = webdriver.Chrome(options=options)
            else:
                # Normal mode
                service = Service(self.driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            
            logger.info("[OK] Driver created successfully")
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create driver: {e}")
            raise
    
    def _create_chrome_options(self) -> Options:
        """Configure Chrome options"""
        options = Options()
        
        # If using debug mode
        if self.use_debug_mode:
            logger.info(f"Connecting to debug port: localhost:{self.debug_port}")
            options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")
            return options
        
        # Normal mode settings
        if self.headless:
            logger.info("Headless mode enabled")
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
        
        # Anti-automation detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Default settings
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        
        return options
    
    def human_delay(self, min_seconds: float = 1.0, max_seconds: float = 2.0) -> None:
        """
        Natural random delay like human behavior
        
        Args:
            min_seconds: Minimum wait time (seconds)
            max_seconds: Maximum wait time (seconds)
        """
        import random
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def quit_driver(self, driver: webdriver.Chrome, kill_chrome: bool = False) -> None:
        """
        Quit driver
        
        Args:
            driver: Selenium driver instance
            kill_chrome: Whether to force kill Chrome process (debug mode only)
        """
        try:
            if driver:
                driver.quit()
                logger.info("Driver quit complete")
            
            # Also terminate Chrome process in debug mode
            if kill_chrome and self.chrome_pid:
                self.kill_chrome_process()
                
        except Exception as e:
            logger.error(f"Failed to quit driver: {e}")
    
    def kill_chrome_process(self) -> None:
        """Force kill Chrome process"""
        try:
            if not self.chrome_pid:
                logger.warning("No Chrome PID to terminate.")
                return
            
            logger.info(f"Terminating Chrome process: PID={self.chrome_pid}")
            
            if platform.system() == "Windows":
                # Terminate specific PID
                subprocess.run(["taskkill", "/F", "/PID", str(self.chrome_pid)], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Terminate all Chrome processes using debug port (safety measure)
                time.sleep(0.5)
                subprocess.run(
                    ["powershell", "-Command", 
                     f"Get-Process chrome -ErrorAction SilentlyContinue | Where-Object {{$_.CommandLine -like '*{self.debug_port}*'}} | Stop-Process -Force"],
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
            else:
                subprocess.run(["kill", "-9", str(self.chrome_pid)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.chrome_pid = None
            logger.info("Chrome process terminated")
            
            # Allow time for process to fully terminate
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"Failed to terminate Chrome process: {e}")


def test_chrome_driver():
    """Test function"""
    import time
    
    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test with debug mode
    chrome = ChromeDriver(headless=False, use_debug_mode=True)
    driver = chrome.create_driver()
    
    try:
        # Visit test page
        print("\nNavigating to Naver...")
        driver.get("https://www.naver.com")
        time.sleep(3)
        
        print("\nClosing in 5 seconds...")
        time.sleep(5)
        
    finally:
        chrome.quit_driver(driver, kill_chrome=True)


if __name__ == "__main__":
    test_chrome_driver()
