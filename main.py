import time
import logging
import json
import os
import gc
import argparse
import csv
from datetime import datetime
from pathlib import Path
from selenium.webdriver.common.by import By
from src.chrome_driver import ChromeDriver
from src.naver_shopping import OptimizedNaverCrawler


def setup_result_logger(log_dir="logs"):
    """Setup result logger for success/failure tracking"""
    # Create logs directory if not exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Create logger
    result_logger = logging.getLogger('result_logger')
    result_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    result_logger.handlers = []
    
    # File handler - logs/result_YYYYMMDD.log
    log_filename = f"{log_dir}/result_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Format: timestamp | status | keyword | url | message
    formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    
    result_logger.addHandler(file_handler)
    
    return result_logger, log_filename


def log_result(logger, status: str, keyword: str, url: str, message: str = ""):
    """
    Log crawling result
    
    Args:
        logger: Logger instance
        status: SUCCESS, FAIL, ERROR
        keyword: Search keyword
        url: Target URL
        message: Additional message (optional)
    """
    log_message = f"{status} | {keyword} | {url} | {message}"
    
    if status == "SUCCESS":
        logger.info(log_message)
    elif status == "FAIL":
        logger.warning(log_message)
    else:  # ERROR
        logger.error(log_message)


def load_config(config_path="config/config.json"):
    """Load config.json file"""
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"[WARNING] Config file not found: {config_path}")
            print("Using default settings.")
            return {
                "headless": False,
                "wait_time": 3,
                "timeout": 10,
                "use_debug_mode": True,
                "debug_port": 9222,
                "profile_path": None
            }
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"[OK] Config file loaded: {config_path}")
            return config
    except Exception as e:
        print(f"[ERROR] Failed to load config file: {e}")
        print("Using default settings.")
        return {
            "headless": False,
            "wait_time": 3,
            "timeout": 10,
            "use_debug_mode": True,
            "debug_port": 9222,
            "profile_path": None
        }


def test_crawler(url_list: dict = {}, config=None, repeat_count: int = 1, rest_minutes: float = 10.0):
    """
    Crawler test (using naver_shopping.py)
    
    Args:
        url_list: URL dictionary to test (URL: [keyword1, keyword2, ...])
        config: Configuration dictionary (auto-load if None)
        repeat_count: Number of times to repeat the entire crawling process (default: 1)
        rest_minutes: Rest time in minutes between each repeat cycle (default: 3.0)
    """
    # Load config
    if config is None:
        config = load_config()
    
    # Build round-robin task list: [(url, keyword), ...]
    # Order: 1st URL's 1st keyword -> 2nd URL's 1st keyword -> ... -> 1st URL's 2nd keyword -> ...
    urls = list(url_list.keys())
    num_urls = len(urls)
    keywords_per_url = 5  # Fixed 5 keywords per URL
    
    task_list = []
    for keyword_idx in range(keywords_per_url):
        for url in urls:
            keywords = url_list[url]
            if keyword_idx < len(keywords):
                task_list.append((url, keywords[keyword_idx]))
    
    total_tasks = len(task_list)
    
    print(f"\n{'='*60}")
    print(f"[SEARCH] Crawler test started")
    print(f"[SEARCH] Number of URLs: {num_urls}")
    print(f"[SEARCH] Keywords per URL: {keywords_per_url}")
    print(f"[SEARCH] Total tasks: {total_tasks}")
    print(f"[SEARCH] Repeat count: {repeat_count} times")
    print(f"[SEARCH] Rest time between cycles: {rest_minutes} minutes")
    print(f"{'='*60}")
    print(f"\n[CONFIG] Current settings:")
    print(f"  - Headless mode: {config.get('headless', False)}")
    print(f"  - Debug mode: {config.get('use_debug_mode', True)} (VBA original method)")
    if config.get('use_debug_mode', True):
        print(f"  - Debug port: {config.get('debug_port', 9222)}")
        profile_path = config.get('profile_path') or os.path.expanduser("~/ChromeTEMP")
        print(f"  - Profile path: {profile_path}")
    print(f"  - Wait time: {config.get('wait_time', 3)} seconds")
    print(f"  - Timeout: {config.get('timeout', 10)} seconds")
    print(f"{'='*60}\n")
    
    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Setup result logger
    result_logger, log_filename = setup_result_logger()
    print(f"[LOG] Result log file: {log_filename}")
    
    # Statistics
    stats = {"success": 0, "fail": 0, "error": 0}
    
    # Process all tasks
    if not url_list:
        print("[WARNING] No URLs to process.")
        return
    
    # Repeat loop
    for cycle in range(1, repeat_count + 1):
        print(f"\n{'#'*60}")
        print(f"[CYCLE] Starting cycle {cycle}/{repeat_count}")
        print(f"{'#'*60}")
        
        for idx, (url, keyword) in enumerate(task_list, 1):
            print(f"\n{'='*60}")
            print(f"[LOOP] Cycle {cycle}/{repeat_count} - Task {idx}/{total_tasks}: '{keyword}'")
            print(f"{'='*60}")
            
            # Create new driver for each keyword
            chrome = ChromeDriver(
                headless=config.get("headless", False),
                use_debug_mode=config.get("use_debug_mode", True),
                debug_port=config.get("debug_port", 9222),
                profile_path=config.get("profile_path")  # None uses ~/ChromeTEMP automatically
            )

            driver = chrome.create_driver()
            
            # Add driver attribute to ChromeDriver object (used by OptimizedNaverCrawler)
            chrome.driver = driver
            
            # Create OptimizedNaverCrawler (naver_shopping.py)
            crawler = OptimizedNaverCrawler(chrome_controller=chrome)

            try:
                # Show login guide only for the first keyword of the first cycle
                if cycle == 1 and idx == 1:
                    print("\n[1] Naver Login (Optional)")
                    print("  - Please login manually in the browser if needed.")
                    # input("  - Press Enter to skip login...")
                
                print(f"\n[2] Search test: '{keyword}'")
                
                # Use _natural_search from naver_shopping.py
                # Automatically: Naver main -> Integrated search -> Shopping tab click
                crawler._natural_search(keyword=keyword, domestic=True)
                
                # Load product list
                crawler._fast_lazy_load()

                # Extract UID from URL
                target_uid = crawler.extract_uid_from_url(url)
                
                if target_uid:
                    print(f"\n[3] Finding target product")
                    print(f"  - URL: {url}")
                    print(f"  - UID (nv_mid): {target_uid}")
                    
                    # Find and click product by nv_mid
                    success = crawler.find_and_click_product_by_uid(target_uid)
                    
                    if success:
                        print(f"\n[OK] Successfully navigated to product page!")
                        print(f"  [LINK] Current URL: {driver.current_url}")
                        
                        # Log success
                        log_result(result_logger, "SUCCESS", keyword, url, f"Product found and clicked (Cycle {cycle})")
                        stats["success"] += 1
                        
                        # Wait briefly (allow user to see result)
                        time.sleep(2)
                    else:
                        print(f"\n[WARNING] Product not found.")
                        
                        # Log fail
                        log_result(result_logger, "FAIL", keyword, url, f"Product not found in search results (Cycle {cycle})")
                        stats["fail"] += 1
                else:
                    print(f"\n[WARNING] Could not extract UID from URL: {url}")
                    
                    # Log fail - UID extraction failed
                    log_result(result_logger, "FAIL", keyword, url, f"Could not extract UID from URL (Cycle {cycle})")
                    stats["fail"] += 1
                    
                    # If UID extraction fails, proceed with existing method
                    print("\n[3] Extracting price comparison product data")
                    data = crawler._extract_store_data(page=1)
                    
                    if data:
                        print(f"\n[OK] {len(data)} stores extracted!")
                        print(f"\n[DATA] Extracted data sample (first 3):")
                        for i, item in enumerate(data[:3], 1):
                            print(f"\n[{i}]")
                            print(f"  Product name: {item.get('상품명', 'N/A')[:50]}")
                            print(f"  Store: {item.get('이름', 'N/A')}")
                            print(f"  Ranking: {item.get('ranking', 'N/A')}")
                            print(f"  Ad: {item.get('광고', 'N/A')}")
                            print(f"  Reviews: {item.get('리뷰수', 'N/A')}")
                            print(f"  Likes: {item.get('찜수', 'N/A')}")
                    else:
                        print("\n[WARNING] Data extraction failed")
                
                print(f"\n[OK] Keyword '{keyword}' processing complete!")
                
            except Exception as e:
                print(f"\n[ERROR] Error processing keyword '{keyword}': {e}")
                import traceback
                traceback.print_exc()
                
                # Log error
                log_result(result_logger, "ERROR", keyword, url, f"{str(e)} (Cycle {cycle})")
                stats["error"] += 1
                
            finally:
                print(f"\nShutting down driver... ({idx}/{total_tasks})")
                # Completely terminate Chrome process (for next keyword processing)
                chrome.quit_driver(driver, kill_chrome=True)
                print("[OK] Driver shutdown complete!")
                
                # Wait briefly if there are more keywords (allow Chrome process to fully terminate)
                if idx < total_tasks:
                    print("\n[WAIT] Preparing for next keyword...")
                    time.sleep(10)  # Allow time for Chrome process to fully terminate
        
        print(f"\n{'='*60}")
        print(f"[CYCLE DONE] Cycle {cycle}/{repeat_count} complete! (Tasks: {total_tasks})")
        print(f"{'='*60}")
        
        # Clear memory after each cycle
        print("\n[MEMORY] Clearing memory...")
        gc.collect()
        print("[MEMORY] Memory cleared!")
        
        # Rest between cycles (except for the last cycle)
        if cycle < repeat_count:
            rest_seconds = int(rest_minutes * 60)
            print(f"\n[REST] Resting for {rest_minutes} minutes ({rest_seconds} seconds)...")
            print(f"[REST] Next cycle starts at: {time.strftime('%H:%M:%S', time.localtime(time.time() + rest_seconds))}")
            
            # Show countdown every 30 seconds
            remaining = rest_seconds
            while remaining > 0:
                if remaining <= 10 or remaining % 30 == 0:
                    print(f"[REST] {remaining} seconds remaining...")
                time.sleep(min(10, remaining))
                remaining -= min(10, remaining)
            
            print("[REST] Rest complete! Starting next cycle...")
    
    print(f"\n{'#'*60}")
    print(f"[DONE] All cycles complete! (Cycles: {repeat_count}, Tasks per cycle: {total_tasks})")
    print(f"[DONE] Total tasks processed: {repeat_count * total_tasks}")
    print(f"{'#'*60}")
    
    # Print statistics
    print(f"\n{'='*60}")
    print(f"[STATS] Final Statistics")
    print(f"{'='*60}")
    print(f"  - SUCCESS: {stats['success']}")
    print(f"  - FAIL: {stats['fail']}")
    print(f"  - ERROR: {stats['error']}")
    print(f"  - Total: {stats['success'] + stats['fail'] + stats['error']}")
    success_rate = (stats['success'] / (stats['success'] + stats['fail'] + stats['error']) * 100) if (stats['success'] + stats['fail'] + stats['error']) > 0 else 0
    print(f"  - Success Rate: {success_rate:.1f}%")
    print(f"{'='*60}")
    print(f"[LOG] Results saved to: {log_filename}")
    # input("\nPress Enter to exit...")



def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Naver Shopping Crawler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py                    # Run once (default)
  python main.py --repeat 10        # Repeat 10 times
  python main.py --repeat 5 --rest 5  # Repeat 5 times with 5 minutes rest
  python main.py -r 10 -t 2         # Short form: repeat 10 times, 2 minutes rest
        '''
    )
    parser.add_argument(
        '-r', '--repeat',
        type=int,
        default=1,
        help='Number of times to repeat the entire crawling process (default: 1)'
    )
    parser.add_argument(
        '-t', '--rest',
        type=float,
        default=10.0,
        help='Rest time in minutes between each cycle (default: 10.0)'
    )
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Load config.json settings
    config = load_config()
    
    url_list = {
        "https://brand.naver.com/sennheiserstore/products/12534300529": [
            "헤드폰 BTD700",
            "BTD700 헤드셋",
            "HDB630 블루투스",
            "젠하이저 HDB630",
            "무선 ANC 헤드폰",
        ],
        "https://smartstore.naver.com/ottempt_4291/products/4665304597": [
            "드립백커피 실속",
            "드립백커피 인기",
            "드립백커피 취향",
            "드립백커피 새벽",
            "드립백커피 농도",
        ],
        "https://smartstore.naver.com/kssinesp/products/6434002841": [
            "접이식 고기 테이블",
            "접이식 가정용 불판",
            "불판 접이식 테이블",
            "가정용 불판 테이블",
            "접이식 테이블 가격",
        ],
        "https://smartstore.naver.com/thenaeun2018/products/4589988752": [
            "네츄럴EX 간식",
            "프리미엄 오리츄",
            "오리츄 프리미엄",
            "수제간식 오리츄",
            "오리츄 수제간식",
        ],
        "https://smartstore.naver.com/glecoleshop/products/10057924203": [
            "개업 액막이",
            "고사 액막이",
            "DIY 북어",
            "DIY 명태",
            "액막이 선물",
        ],
    }
    
    # Run crawler test with command line arguments
    test_crawler(
        url_list=url_list, 
        config=config, 
        repeat_count=args.repeat,
        rest_minutes=args.rest
    )
