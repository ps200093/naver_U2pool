"""
Optimized Naver Shopping Crawler
"""

from selenium.webdriver.common.by import By
import json
import pandas as pd
import time
import random
from urllib.parse import urlparse, parse_qs


class OptimizedNaverCrawler:
    """Speed-optimized Naver Shopping Crawler"""
    
    def __init__(self, chrome_controller):
        self.chrome = chrome_controller
        self.driver = chrome_controller.driver
    
    @staticmethod
    def extract_uid_from_url(url):
        """
        Extract product UID (nv_mid) from Naver Shopping URL
        
        Supported URL formats:
            1. SmartStore: https://smartstore.naver.com/oroda_mall/products/7197769400
            2. Shopping Catalog: https://search.shopping.naver.com/catalog/57407585768
            3. Query parameter: ?n_media_id=12345 or ?nvMid=12345
        
        Args:
            url: Naver Shopping product URL
        
        Returns:
            str: Product UID (nv_mid)
        """
        try:
            # Parse URL
            parsed = urlparse(url)
            
            # 1. Extract from /products/{uid} format (SmartStore)
            if '/products/' in parsed.path:
                uid = parsed.path.split('/products/')[-1].split('/')[0].split('?')[0]
                return uid
            
            # 2. Extract from /catalog/{uid} or /cattalog/{uid} format (Shopping Catalog)
            if '/catalog/' in parsed.path or '/cattalog/' in parsed.path:
                # Extract number after catalog or cattalog
                parts = parsed.path.split('/')
                for i, part in enumerate(parts):
                    if part in ['catalog', 'cattalog'] and i + 1 < len(parts):
                        uid = parts[i + 1].split('?')[0]
                        if uid.isdigit():
                            return uid
            
            # 3. Try extracting from query parameters
            query_params = parse_qs(parsed.query)
            if 'n_media_id' in query_params:
                return query_params['n_media_id'][0]
            if 'nvMid' in query_params:
                return query_params['nvMid'][0]
            
            return None
        except Exception as e:
            print(f"    [WARNING] UID extraction failed: {e}")
            return None
    
    def crawl_page(self, keyword, page=1, domestic=True, first_search=False):
        """
        Single page crawling
        
        Args:
            keyword: Search keyword
            page: Page number
            domestic: True=Domestic, False=International
            first_search: Whether this is the first search
        
        Returns:
            list: Store data list
        """
        from urllib.parse import quote
        
        print(f"  [PAGE] Loading page {page}...")
        
        if first_search and page == 1:
            # First search: Naver integrated search -> Shopping tab click (natural method)
            self._natural_search(keyword, domestic)
        else:
            # VBA: Navigate to page by button click
            self._click_page_button(page)
        
        # Lazy loading handling (VBA: scroll to load products)
        self._fast_lazy_load()
        
        # Data extraction (VBA: For Each store In stores)
        data = self._extract_store_data(page)
        
        print(f"  [OK] {len(data)} stores extracted")
        
        return data
    
    
    def _natural_search(self, keyword, domestic=True):
        """
        Natural search (simple like VBA original!)
        VBA original logic:
        1. If shopping search box exists -> direct input
        2. If not -> integrated search (VBA URL parameters) -> shopping tab click
        """
        from urllib.parse import quote
        from selenium.webdriver.common.keys import Keys
        
        print("=" * 70)
        print("[SEARCH] Search started (VBA original method)")
        print("=" * 70)
        
        # VBA original: First check if shopping search box exists
        print(f"  [SEARCH] Checking for shopping search box...")
        shopping_search_box = None
        
        # Only use search box if on shopping page
        current_url = self.driver.current_url
        if "search.shopping.naver.com" in current_url:
            try:
                # VBA: SEL.FindElementByCss("._searchInput_search_text_83jy9", 0)
                shopping_search_box = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "._searchInput_search_text_83jy9"
                )
                if not shopping_search_box.is_displayed():
                    shopping_search_box = None
            except:
                shopping_search_box = None
        
        # If shopping search box exists, input directly (VBA original)
        if shopping_search_box:
            print(f"  [OK] Shopping search box found! Direct input...")
            try:
                shopping_search_box.clear()
                time.sleep(random.uniform(0.3, 0.5))
                
                # Input keyword
                for char in keyword:
                    shopping_search_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                time.sleep(random.uniform(0.5, 1))
                
                # Press Enter
                shopping_search_box.send_keys(Keys.RETURN)
                time.sleep(random.uniform(1, 2))
                
                print(f"  [OK] Search complete!")
                return
            except Exception as e:
                print(f"  [WARNING] Direct search failed: {e}, switching to integrated search...")
        
        # If no shopping search box, start from integrated search (VBA original)
        print(f"  [SEARCH] Moving to integrated search...")
        
        # Check current page
        current_url = self.driver.current_url
        print(f"  DEBUG: Current URL: {current_url}")
        
        # If not on Naver main, navigate to main (more natural)
        if "naver.com" not in current_url or "search.shopping.naver.com" in current_url:
            print(f"  [HOME] Navigating to Naver main first...")
            self.driver.get("https://www.naver.com")
            time.sleep(random.uniform(1, 2))
        
        encoded = quote(keyword)
        # Same URL parameters as VBA original!
        search_url = f"https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&ssc=tab.nx.all&query={encoded}"
        
        print(f"  DEBUG: Search URL: {search_url}")
        self.driver.get(search_url)
        time.sleep(random.uniform(2, 3))
        
        print(f"  DEBUG: URL after navigation: {self.driver.current_url}")
        print(f"  DEBUG: Page title: {self.driver.title}")
        
        # Check for error page
        if "오류" in self.driver.title or "error" in self.driver.title.lower():
            print(f"  [WARNING] Error page detected!")
            print(f"  [TIP] Solutions:")
            print(f"     1. Check login status")
            print(f"     2. Close browser and restart")
            print(f"     3. Try again later")
            return
        
        # VBA original: Try 10 times to find shopping tab
        print(f"  [CART] Finding shopping tab...")
        
        # Record current window count (to check if new window opened from shopping tab click)
        initial_window_count = len(self.driver.window_handles)
        print(f"  DEBUG: Initial window count: {initial_window_count}")
        
        for attempt in range(10):
            # VBA: d.wait 1000 (1 second wait)
            time.sleep(1)
            
            current_window_count = len(self.driver.window_handles)
            print(f"  DEBUG: Attempt {attempt + 1}/10, current window count: {current_window_count}")
            
            # VBA: If SEL.Windows.Count = 1 Then
            # Modified: Compare with initial window count
            if current_window_count == initial_window_count:
                # Find shopping tab (try multiple selectors)
                shopping_tab = None
                
                # Selector list (in priority order)
                selectors = [
                    # 1. role="tab" + class="tab" (latest Naver)
                    'a[role="tab"].tab',
                    # 2. role="tab" attribute only
                    'a[role="tab"]',
                    # 3. Old version selector
                    '.flick_bx a',
                    # 4. XPath text search (last resort)
                    None  # XPath handled separately
                ]
                
                try:
                    for selector in selectors:
                        if selector:
                            # CSS selector
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            print(f"  DEBUG: Found {len(elements)} elements with selector '{selector}'")
                            
                            for elem in elements:
                                try:
                                    elem_text = elem.text.strip()
                                    if elem_text:
                                        print(f"  DEBUG: Element text: '{elem_text}'")
                                    if elem_text == '쇼핑':
                                        shopping_tab = elem
                                        print(f"  [OK] Shopping tab found! (selector: {selector}, attempt {attempt + 1}/10)")
                                        break
                                except:
                                    continue
                            
                            if shopping_tab:
                                break
                    
                    # If CSS selectors fail, try XPath
                    if not shopping_tab:
                        print(f"  DEBUG: Searching for shopping tab with XPath...")
                        xpath_selectors = [
                            "//a[@role='tab' and contains(text(), '쇼핑')]",
                            "//a[contains(@class, 'tab') and contains(text(), '쇼핑')]",
                            "//a[contains(text(), '쇼핑')]"
                        ]
                        
                        for xpath in xpath_selectors:
                            try:
                                elements = self.driver.find_elements(By.XPATH, xpath)
                                print(f"  DEBUG: Found {len(elements)} elements with XPath")
                                if elements:
                                    shopping_tab = elements[0]
                                    print(f"  [OK] Shopping tab found! (XPath, attempt {attempt + 1}/10)")
                                    break
                            except:
                                continue
                
                except Exception as e:
                    print(f"  DEBUG: Error finding shopping tab: {e}")
                
                if shopping_tab:
                    # Save original window
                    original_windows = self.driver.window_handles
                    
                    # VBA: ShoppingTab.Click: d.wait 1000
                    try:
                        shopping_tab.click()
                        print(f"  [CLICK] Shopping tab clicked!")
                        time.sleep(2)  # 1 sec -> 2 sec (time for new window to open)
                        
                        # VBA: SEL.SwitchToNextWindow
                        new_windows = self.driver.window_handles
                        if len(new_windows) > len(original_windows):
                            for window in new_windows:
                                if window not in original_windows:
                                    self.driver.switch_to.window(window)
                                    print(f"  [OK] Switched to shopping page!")
                                    print(f"  DEBUG: New window URL: {self.driver.current_url}")
                                    break
                        
                        break  # Exit loop on success
                    except Exception as e:
                        print(f"  [WARNING] Click error: {e}")
                        import traceback
                        traceback.print_exc()
            else:
                # New window opened (shopping tab click succeeded)
                print(f"  [OK] New window detected! (windows {initial_window_count} -> {current_window_count})")
                break
        
        print("=" * 70)
        print("[SEARCH] Search complete")
        print("=" * 70)
        
        # VBA: If SEL.Windows.Count = 1 Then GoTo passKeyword
        # Modified: Compare with initial window count
        final_window_count = len(self.driver.window_handles)
        if final_window_count == initial_window_count:
            print(f"  [WARNING] Shopping tab click failed! (no window count change: {initial_window_count})")
            print(f"  [INFO] Attempting direct navigation to shopping URL...")
            
            # Last resort: Navigate directly to shopping search URL
            from urllib.parse import quote
            encoded = quote(keyword)
            shopping_url = f"https://search.shopping.naver.com/search/all?where=all&frm=NVSCTAB&query={encoded}"
            print(f"  DEBUG: Direct navigation URL: {shopping_url}")
            self.driver.get(shopping_url)
            time.sleep(2)
            return
        
        # VBA: d.wait 1000
        time.sleep(2)  # 1 sec -> 2 sec (wait for page loading)
        
        # Check error after shopping page loads
        print(f"  [SEARCH] Checking shopping page status...")
        print(f"  DEBUG: Current URL: {self.driver.current_url}")
        print(f"  DEBUG: Page title: {self.driver.title}")
        
        # Detect error page
        if "오류" in self.driver.title or "error" in self.driver.title.lower():
            print(f"  [WARNING] [WARNING] [WARNING] Error page detected! [WARNING] [WARNING] [WARNING]")
            print(f"  ")
            print(f"  [ALERT] Naver detected automation!")
            print(f"  ")
            print(f"  [TIP] Solutions:")
            print(f"     1. Manually navigate to normal page in browser")
            print(f"     2. Or press Enter to skip to next keyword")
            print(f"  ")
            input("  [PAUSE] Press Enter to continue...")
            return
    
    
    def _click_page_button(self, target_page):
        """
        VBA: Sub NextPageNavigation(SEL As ChromeDriver, Page As Long)
        Pagination - Navigate to page using Selenium click
        
        Args:
            target_page: Page number to navigate to
        """
        print(f"  [BUTTON] Navigating to page {target_page}...")
        
        try:
            # Try multiple selectors to find page button
            selectors = [
                # Use data-shp-contents-id attribute (most accurate)
                f"a.pagination_btn_page__utqBz[data-shp-contents-id='{target_page}']",
                # Pagination button with target_page text
                f"a.pagination_btn_page__utqBz",
                # Backup: general pagination link
                ".pagination_num__qsa2U a"
            ]
            
            page_button = None
            used_selector = None
            
            # Try first selector (most accurate method)
            try:
                page_button = self.driver.find_element(By.CSS_SELECTOR, selectors[0])
                used_selector = selectors[0]
                print(f"  [OK] Button found with data-shp-contents-id")
            except:
                # Second method: Find all buttons and match by text
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selectors[1])
                    for btn in buttons:
                        if btn.text.strip() == str(target_page):
                            page_button = btn
                            used_selector = selectors[1]
                            print(f"  [OK] Button found with text matching")
                            break
                except:
                    pass
            
            if not page_button:
                print(f"  [ERROR] Could not find page {target_page} button.")
                return False
            
            # Scroll until button is visible
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", page_button)
            time.sleep(0.5)
            
            # Try clicking (multiple methods)
            click_success = False
            
            # Method 1: Normal click
            try:
                page_button.click()
                click_success = True
                print(f"  [OK] Normal click succeeded")
            except Exception as e1:
                print(f"  [WARNING] Normal click failed: {e1}")
                
                # Method 2: JavaScript click
                try:
                    self.driver.execute_script("arguments[0].click();", page_button)
                    click_success = True
                    print(f"  [OK] JavaScript click succeeded")
                except Exception as e2:
                    print(f"  [WARNING] JavaScript click failed: {e2}")
                    
                    # Method 3: ActionChains click
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(self.driver)
                        actions.move_to_element(page_button).click().perform()
                        click_success = True
                        print(f"  [OK] ActionChains click succeeded")
                    except Exception as e3:
                        print(f"  [ERROR] ActionChains click failed: {e3}")
            
            if not click_success:
                print(f"  [ERROR] All click methods failed")
                return False
            
            # Wait for page loading
            time.sleep(2)
            
            # Scroll to top
            print(f"  [UP] Scrolling to top of page...")
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Wait for basic page loading
            self._wait_for_page_load()
            
            # Verify page transition
            try:
                # Find active page button
                active_button = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    ".pagination_num__qsa2U a.pagination_on__hQbxh, .pagination_on__hQbxh"
                )
                active_page_num = active_button.text.strip()
                
                if active_page_num == str(target_page):
                    print(f"  [OK] Page {target_page} transition confirmed!")
                else:
                    print(f"  [WARNING] Page mismatch: requested={target_page}, actual={active_page_num}")
                    return False
            except Exception as e:
                print(f"  [WARNING] Page verification failed: {e}")
                # Continue to product verification even if active button not found
            
            # Lazy load to load all 40 products
            print(f"  [SCROLL] Loading products for page {target_page} (target: 40)...")
            self._fast_lazy_load(max_attempts=20)
            
            # Final check: product count
            products = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".product_item__KQayS, .adProduct_item__T7utB"
            )
            
            if len(products) > 0:
                print(f"  [OK] {len(products)} products loaded")
                
                # Warning if less than 40
                if len(products) < 40:
                    print(f"  [WARNING] Fewer products than expected (target: 40, actual: {len(products)})")
                    print(f"      -> May be last page or only partial products available.")
                
                return True
            else:
                print(f"  [WARNING] No products detected!")
                return False
            
        except Exception as e:
            print(f"  [ERROR] Page navigation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    def _wait_for_page_load(self):
        """
        VBA: Sub WaitForLanding(SEL As ChromeDriver)
        Wait for page loading
        """
        # VBA: SEL.ExecuteScript ("window.scrollBy(0, 20000)"): d.wait 1000
        try:
            self.driver.execute_script("window.scrollBy(0, 20000)")
            time.sleep(1)
        except:
            pass
        
        # VBA: Set LandingObject = SEL.FindElementByClass("basicList_list_basis__uNBZx", 0)
        max_wait = 10
        for i in range(max_wait):
            try:
                list_element = self.driver.find_element(By.CLASS_NAME, "basicList_list_basis__uNBZx")
                if list_element:
                    return  # Loading complete
            except:
                pass
            
            # VBA: No result checker
            try:
                no_result = self.driver.find_element(By.CSS_SELECTOR, ".noResultWithBestResults_svg_noresult__uF7vF")
                if no_result:
                    print(f"  [WARNING] No search results")
                    return
            except:
                pass
            
            time.sleep(0.5)
        
        # Verify page loaded properly
        try:
            # Check if shopping search results exist
            time.sleep(1)
            products = self.driver.find_elements(By.CSS_SELECTOR, ".product_item__KQayS")
            print(f"  [OK] Shopping page normal! ({len(products)} products detected)")
        except Exception as e:
            print(f"  [WARNING] Page loading verification failed: {e}")
        
        time.sleep(1)
        
        # Handle book search case (VBA original)
        try:
            # VBA: SEL.FindElementByCss(".bookSearchNotice_show_all__unpDH", 0).Click
            book_notice = self.driver.find_element(
                By.CSS_SELECTOR,
                ".bookSearchNotice_show_all__unpDH"
            )
            book_notice.click()
            print(f"  [BOOK] Book search detected! Switching to price comparison...")
            time.sleep(1)
        except:
            pass
    
    def _fast_lazy_load(self, max_attempts=20):
        """Fast lazy loading handling (natural scrolling)"""
        print("=" * 70)
        print("[SCROLL] DEBUG: _fast_lazy_load() started")
        print(f"  DEBUG: Current URL: {self.driver.current_url}")
        print(f"  DEBUG: Initial scroll position: {self.driver.execute_script('return window.pageYOffset')}")
        print("=" * 70)
        
        # Wait for page loading (extension: search-content.js line 323)
        print(f"  [WAIT] Waiting for initial page loading (3 seconds)...")
        time.sleep(3)  # 2 sec -> 3 sec
        
        # Check Next.js data loading (max 10 seconds)
        print(f"  [SEARCH] Checking Next.js data loading...")
        data_loaded = False
        for i in range(20):  # Max 20 attempts (10 seconds)
            try:
                has_data = self.driver.execute_script("""
                    return window.__NEXT_DATA__ 
                        && window.__NEXT_DATA__.props 
                        && window.__NEXT_DATA__.props.pageProps;
                """)
                if has_data:
                    data_loaded = True
                    print(f"  [OK] Next.js data loading complete! (attempt {i+1}/20)")
                    break
            except Exception as e:
                if i == 0:  # Only print error on first attempt
                    print(f"  DEBUG: Next.js check error: {e}")
            time.sleep(0.5)
        
        if not data_loaded:
            # Detailed failure analysis
            print(f"  [WARNING] Next.js data loading failed!")
            try:
                # Check current URL
                current_url = self.driver.current_url
                print(f"  DEBUG: Current URL: {current_url}")
                
                # Check if window.__NEXT_DATA__ exists
                has_next_data = self.driver.execute_script("return typeof window.__NEXT_DATA__ !== 'undefined';")
                print(f"  DEBUG: window.__NEXT_DATA__ exists: {has_next_data}")
                
                if has_next_data:
                    # Check __NEXT_DATA__ structure
                    has_props = self.driver.execute_script("return window.__NEXT_DATA__ && window.__NEXT_DATA__.props !== undefined;")
                    print(f"  DEBUG: __NEXT_DATA__.props exists: {has_props}")
                    
                    if has_props:
                        has_pageProps = self.driver.execute_script("return window.__NEXT_DATA__.props.pageProps !== undefined;")
                        print(f"  DEBUG: __NEXT_DATA__.props.pageProps exists: {has_pageProps}")
                        
                        # Check pageProps keys
                        pageProps_keys = self.driver.execute_script("""
                            if (window.__NEXT_DATA__ && window.__NEXT_DATA__.props && window.__NEXT_DATA__.props.pageProps) {
                                return Object.keys(window.__NEXT_DATA__.props.pageProps);
                            }
                            return [];
                        """)
                        print(f"  DEBUG: pageProps keys: {pageProps_keys}")
                
                # Check if on shopping page
                if 'search.shopping.naver.com' not in current_url:
                    print(f"  [WARNING] Not on shopping page! (integrated search or other page)")
                    print(f"  [TIP] Please verify shopping tab was clicked.")
                
            except Exception as debug_error:
                print(f"  DEBUG: Error during debugging: {debug_error}")
            
            print(f"  [INFO] Continuing... (will work normally if product list exists)")
        
        target_count = 40  # Target count per page
        no_change_count = 0  # Counter for no changes
        prev_item_count = 0  # Previous item count
        
        for attempt in range(max_attempts):
            # Wait briefly before finding elements (allow DOM update time)
            time.sleep(0.3)
            
            # Check current item count
            items = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".product_item__KQayS, .adProduct_item__T7utB"
            )
            current_item_count = len(items)
            
            print(f"  DEBUG: Lazy load attempt {attempt + 1}/{max_attempts} - item count: {current_item_count}/{target_count}")
            
            # Additional debugging: Check by CSS selector
            if attempt == 0 and current_item_count == 0:
                product_items = self.driver.find_elements(By.CSS_SELECTOR, ".product_item__KQayS")
                ad_items = self.driver.find_elements(By.CSS_SELECTOR, ".adProduct_item__T7utB")
                print(f"  DEBUG: Regular products: {len(product_items)}, Ad products: {len(ad_items)}")
                
                # Try alternative selector
                alt_items = self.driver.find_elements(By.CSS_SELECTOR, "[class*='product_item'], [class*='adProduct_item']")
                print(f"  DEBUG: Products found with alternative selector: {len(alt_items)}")
            
            # Check if target reached
            if current_item_count >= target_count:
                print(f"  [OK] Target item count reached!")
                break
            
            # Detect no change (exit after 3 consecutive no changes)
            if current_item_count == prev_item_count:
                no_change_count += 1
                print(f"  [WARNING] No change in product count ({no_change_count}/3)")
                
                if no_change_count >= 3:
                    print(f"  [WARNING] 3 consecutive no changes - assuming no more products to load")
                    print(f"  [INFO] Proceeding with current {current_item_count} products.")
                    break
            else:
                no_change_count = 0  # Reset counter on change
            
            prev_item_count = current_item_count
            
            # Natural scrolling (smooth behavior - extension method)
            scroll_before = self.driver.execute_script('return window.pageYOffset')
            page_height = self.driver.execute_script('return document.body.scrollHeight')
            
            # Use smooth scrolling
            self.driver.execute_script("""
                window.scrollTo({
                    top: window.pageYOffset + 800,
                    behavior: 'smooth'
                });
            """)
            
            # Allow time for scroll to apply (smooth scroll is animated)
            time.sleep(0.5)
            
            scroll_after = self.driver.execute_script('return window.pageYOffset')
            print(f"  DEBUG: Scroll {scroll_before} -> {scroll_after} (page height: {page_height})")
            
            # If scroll no longer progresses (end of page)
            if scroll_before == scroll_after:
                print(f"  [WARNING] Scroll no longer progressing (end of page)")
                # Wait once more and check elements
                time.sleep(1.5)
                final_items = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    ".product_item__KQayS, .adProduct_item__T7utB"
                )
                print(f"  [INFO] Proceeding with final {len(final_items)} products.")
                break
            
            # Random wait time (1 sec ~ 1.8 sec - more generous)
            random_delay = 1.0 + random.random() * 0.8
            time.sleep(random_delay)
            
            # Wait a bit more every 5 attempts (pretend to read)
            if attempt % 5 == 0 and attempt > 0:
                time.sleep(random.uniform(1.0, 2.0))
    
    def find_and_click_product_by_uid(self, target_uid, max_pages=5, max_scroll_attempts=20):
        """
        Find and click product by UID (search up to 5 pages)
        
        Supports various ID types:
        - nv_mid: Catalog product ID
        - catalog_nv_mid: Catalog product ID (alternative)
        - chnl_prod_no: SmartStore channel product number
        
        Args:
            target_uid: Product UID to find (nv_mid or chnl_prod_no)
            max_pages: Maximum pages to search (default: 5)
            max_scroll_attempts: Maximum scroll attempts per page
        
        Returns:
            bool: Success status
        """
        print(f"\n{'='*70}")
        print(f"[TARGET] Finding product: target_uid={target_uid} (max {max_pages} pages)")
        print(f"   (checking nv_mid, catalog_nv_mid, chnl_prod_no)")
        print(f"{'='*70}")
        
        # Search multiple pages
        for page in range(1, max_pages + 1):
            print(f"\n[PAGE] Searching page {page}...")
            
            # Page navigation needed from page 2 (includes lazy load)
            if page > 1:
                success = self._click_page_button(page)
                if not success:
                    print(f"  [WARNING] Failed to navigate to page {page}, ending search")
                    break
            else:
                # Page 1 loads products via lazy loading
                print(f"  [SCROLL] Loading page 1 products (target: 40)...")
                self._fast_lazy_load(max_attempts=max_scroll_attempts)
            
            try:
                # Get all product elements
                store_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    ".product_item__KQayS, .adProduct_item__T7utB"
                )
                
                print(f"  [BOX] Found {len(store_elements)} products on page {page} (target: 40)")
                
                # Warning if less than 40
                if len(store_elements) < 40:
                    print(f"  [WARNING] Fewer products than expected! May be last page or loading issue.")
                
                # Check ID of each product
                for idx, store in enumerate(store_elements):
                    try:
                        # Find product name link
                        product_link = store.find_element(
                            By.CSS_SELECTOR, 
                            ".product_link__aFnaq, .adProduct_link__hNwpz"
                        )
                        
                        # Extract multiple IDs from data-shp-contents-dtl
                        contents_dtl = product_link.get_attribute('data-shp-contents-dtl')
                        
                        if contents_dtl:
                            try:
                                dtl_array = json.loads(contents_dtl)
                                
                                # Extract multiple ID types
                                id_fields = {
                                    'nv_mid': None,
                                    'catalog_nv_mid': None,
                                    'chnl_prod_no': None
                                }
                                
                                for obj in dtl_array:
                                    key = obj.get('key')
                                    if key in id_fields and obj.get('value'):
                                        id_fields[key] = str(obj['value'])
                                
                                # Debug: Print ID info for all products
                                id_info = ", ".join([f"{k}={v}" for k, v in id_fields.items() if v])
                                print(f"    [{idx+1}] {id_info}")
                                
                                # Compare target_uid with all IDs
                                matched = False
                                matched_field = None
                                
                                for field_name, field_value in id_fields.items():
                                    if field_value and field_value == str(target_uid):
                                        matched = True
                                        matched_field = field_name
                                        break
                                
                                if matched:
                                    print(f"\n  [OK] Matching product found! ({matched_field}={target_uid})")
                                    print(f"     Page: {page}, Index: {idx+1}")
                                    
                                    # Print product info
                                    try:
                                        product_name = product_link.text.strip()
                                        print(f"  [BOX] Product name: {product_name[:50]}...")
                                    except:
                                        pass
                                    
                                    # Scroll to product
                                    self.driver.execute_script(
                                        "arguments[0].scrollIntoView({block: 'center'});", 
                                        store
                                    )
                                    time.sleep(0.5)
                                    
                                    # Click
                                    print(f"  [CLICK] Clicking product...")
                                    product_link.click()
                                    time.sleep(2)
                                    
                                    print(f"  [OK] Navigation to product page complete!")
                                    print(f"  [LINK] Current URL: {self.driver.current_url}")
                                    return True
                            
                            except json.JSONDecodeError:
                                continue
                    
                    except Exception as e:
                        continue
                
                print(f"  [SKIP] Product not found on page {page}.")
            
            except Exception as e:
                print(f"  [WARNING] Error searching page {page}: {e}")
                continue
        
        print(f"\n  [ERROR] Searched {max_pages} pages but could not find product with target_uid={target_uid}.")
        return False
    
    def _extract_store_data(self, page=1):
        """
        Iterate through product elements on screen and extract store info (VBA original method)
        VBA: For Each Store In Stores
        
        Args:
            page: Current page number (for ranking offset calculation)
        """
        try:
            print(f"  [SEARCH] Step 1: Starting product element extraction...")
            
            # === Step 1: Extract TalkTalk ID from JSON (VBA: lines 631-662) ===
            talk_id_dict = {}
            try:
                script = self.driver.find_element(By.ID, "__NEXT_DATA__")
                data = json.loads(script.get_attribute('innerText'))
                products = data.get('props', {}).get('pageProps', {}).get('initialState', {}).get('products', {}).get('list', [])
                
                # VBA: For Each JsonStore In JSON(...)
                for product in products:
                    item = product.get('item', {})
                    product_name = item.get('productName', '')
                    talk_id = item.get('mallInfoCache', {}).get('talkAccountId', '')
                    
                    # VBA: If StoreId <> "" And TalkStore <> "" Then
                    if product_name and talk_id:
                        talk_id_dict[product_name] = talk_id
                
                print(f"  [OK] {len(talk_id_dict)} TalkTalk IDs extracted")
            except Exception as e:
                print(f"  [WARNING] TalkTalk ID extraction failed: {e}")
            
            # === Step 2: Extract store info from screen elements ===
            # VBA: Set Stores = SEL.FindElementsByCss(".product_item__KQayS, .adProduct_item__T7utB", 0)
            store_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".product_item__KQayS, .adProduct_item__T7utB"
            )
            
            print(f"  [OK] Total product elements: {len(store_elements)}")
            
            results = []
            success_count = 0  # Successfully processed product counter
            
            # Debug: Print ranking info for first product
            if len(store_elements) > 0:
                try:
                    first_store = store_elements[0]
                    first_link = first_store.find_element(By.CSS_SELECTOR, "a[data-shp-contents-id]")
                    print(f"  [DEBUG] First product link attributes:")
                    print(f"    - data-shp-contents-id: {first_link.get_attribute('data-shp-contents-id')}")
                    print(f"    - data-shp-contents-grp: {first_link.get_attribute('data-shp-contents-grp')}")
                    print(f"    - data-shp-contents-rank: {first_link.get_attribute('data-shp-contents-rank')}")
                    dtl = first_link.get_attribute('data-shp-contents-dtl')
                    if dtl:
                        print(f"    - data-shp-contents-dtl (full):")
                        try:
                            dtl_parsed = json.loads(dtl)
                            for item in dtl_parsed:
                                print(f"      * {item.get('key')}: {item.get('value')}")
                        except:
                            print(f"      (parse failed) {dtl}")
                    else:
                        print(f"    - data-shp-contents-dtl: None")
                except Exception as e:
                    print(f"  [WARNING] [DEBUG] First product link check failed: {e}")
            
            # VBA: For Each Store In Stores
            for idx, store in enumerate(store_elements):
                try:
                    # VBA: Store.ScrollIntoView
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", store)
                    time.sleep(0.05)  # Short wait
                    
                    # VBA: StoreAddress = Store.FindElementByCss(".product_mall_title__sJPEp a", 0).Attribute("href")
                    try:
                        mall_link = store.find_element(By.CSS_SELECTOR, ".product_mall_title__sJPEp a, .adProduct_mall__grJaU")
                        store_url = mall_link.get_attribute('href')
                    except:
                        continue  # Skip if no store link
                    
                    # VBA: If InStr(StoreAddress, "naver") = 0 Then GoTo pass
                    if 'naver' not in store_url:
                        continue
                    
                    # Filter SmartStore only
                    if 'smartstore.naver.com' not in store_url and 'brand.naver.com' not in store_url:
                        continue
                    
                    # VBA: StoreName = Store.FindElementByCss(".product_mall__0cRyd", 0).Text
                    try:
                        mall_name_elem = store.find_element(By.CSS_SELECTOR, ".product_mall__0cRyd, .adProduct_mall__grJaU, .product_catalog__FbLL3")
                        mall_name = mall_name_elem.text.strip()
                        
                        # VBA: If StoreName = "Lowest Price by Mall" Then GoTo pass
                        if mall_name in ["쇼핑몰별 최저가", "브랜드 카탈로그"]:
                            continue
                    except:
                        mall_name = ""
                    
                    # VBA: ProductName = Store.FindElementByCss(".product_link__aFnaq", 0).Text
                    try:
                        product_link = store.find_element(By.CSS_SELECTOR, ".product_link__aFnaq, .adProduct_link__hNwpz")
                        product_name = product_link.text.strip()
                        product_url = product_link.get_attribute('href')
                    except:
                        continue
                    
                    # Extract Store ID (VBA logic)
                    store_id = ''
                    if 'smartstore.naver.com%2F' in store_url:
                        # URL encoded case
                        store_id = store_url.split('smartstore.naver.com%2F')[1].split('&')[0]
                    elif 'smartstore.naver.com/' in store_url:
                        # Normal case
                        store_id = store_url.split('smartstore.naver.com/')[1].split('/')[0].split('?')[0]
                    elif 'brand.naver.com/' in store_url:
                        store_id = store_url.split('brand.naver.com/')[1].split('/')[0].split('?')[0]
                    
                    if not store_id:
                        continue
                    
                    # Check if brand store
                    is_brand = 'brand.naver.com' in store_url
                    
                    # TalkTalk ID matching
                    talk_id = talk_id_dict.get(product_name, '')
                    
                    # Extension: Ranking info extraction (search-content.js lines 471-596)
                    ranking = None
                    is_ad = False
                    price = 0  # Initialize price
                    nv_mid = None  # Initialize nv_mid
                    
                    try:
                        # Find ranking attribute from product name link (VBA: product_link already found above)
                        product_link_elem = product_link  # Reuse already found product name link
                        contents_grp = product_link_elem.get_attribute('data-shp-contents-grp')
                        contents_rank = product_link_elem.get_attribute('data-shp-contents-rank')
                        contents_dtl = product_link_elem.get_attribute('data-shp-contents-dtl')
                        
                        # Ad status
                        is_ad = (contents_grp == 'ad')
                        
                        if success_count < 3:
                            print(f"    [DEBUG] Success {success_count}: contents_grp={contents_grp}, is_ad={is_ad}")
                        
                        # Extension method: Extract exact ranking by parsing contentsDtl JSON
                        rank_offset = (page - 1) * 40
                        
                        if contents_dtl:
                            try:
                                dtl_array = json.loads(contents_dtl)
                                
                                # Extract nv_mid (already declared above, don't redeclare!)
                                # Try both 'nv_mid' and 'catalog_nv_mid'
                                nv_mid_obj = next((obj for obj in dtl_array if obj.get('key') in ['nv_mid', 'catalog_nv_mid']), None)
                                if nv_mid_obj and nv_mid_obj.get('value'):
                                    nv_mid = str(nv_mid_obj['value'])
                                    if success_count < 3:
                                        print(f"    [OK] Success {success_count}: nv_mid extraction succeeded ({nv_mid_obj.get('key')}) - {nv_mid}")
                                elif success_count < 3:
                                    print(f"    [WARNING] Success {success_count}: nv_mid extraction failed - nv_mid_obj={nv_mid_obj}")
                                    # Print all keys in dtl_array
                                    all_keys = [obj.get('key') for obj in dtl_array]
                                    print(f"    [LIST] Success {success_count}: keys in dtl_array: {all_keys}")
                                
                                # Extract price
                                price_obj = next((obj for obj in dtl_array if obj.get('key') == 'price'), None)
                                if price_obj and price_obj.get('value'):
                                    try:
                                        price = int(price_obj['value'])
                                    except:
                                        price = 0
                                
                                if is_ad:
                                    # For ads: ad_expose_order
                                    ad_order_obj = next((obj for obj in dtl_array if obj.get('key') == 'ad_expose_order'), None)
                                    if ad_order_obj and ad_order_obj.get('value'):
                                        ranking = int(ad_order_obj['value']) + rank_offset
                                        if success_count < 3:
                                            print(f"    [OK] Success {success_count}: Ad ranking extracted - ad_expose_order={ad_order_obj.get('value')}, offset={rank_offset}, final={ranking}")
                                else:
                                    # For regular products: organic_expose_order
                                    organic_order_obj = next((obj for obj in dtl_array if obj.get('key') == 'organic_expose_order'), None)
                                    if organic_order_obj and organic_order_obj.get('value'):
                                        ranking = int(organic_order_obj['value']) + rank_offset
                                        if success_count < 3:
                                            print(f"    [OK] Success {success_count}: Organic ranking extracted - organic_expose_order={organic_order_obj.get('value')}, offset={rank_offset}, final={ranking}")
                                    elif success_count < 3:
                                        print(f"    [WARNING] Success {success_count}: Could not find organic_expose_order")
                                
                                if ranking is None and success_count < 3:
                                    print(f"    [WARNING] Success {success_count}: JSON parsed but ranking is None (is_ad={is_ad})")
                                    
                            except Exception as json_err:
                                # Use contents_rank as fallback if JSON parsing fails
                                if success_count < 3:
                                    print(f"    [WARNING] Success {success_count}: JSON parsing failed - {json_err}")
                                if contents_rank:
                                    ranking = int(contents_rank) + rank_offset
                                    if success_count < 3:
                                        print(f"    [INFO] Success {success_count}: Using contents_rank as fallback - {ranking}")
                        elif contents_rank:
                            # Use contents_rank if contentsDtl doesn't exist
                            ranking = int(contents_rank) + rank_offset
                            if success_count < 3:
                                print(f"    [INFO] Success {success_count}: No contentsDtl, using contents_rank - {ranking}")
                        else:
                            if success_count < 3:
                                print(f"    [WARNING] Success {success_count}: Both contents_dtl and contents_rank are missing")
                            
                    except Exception as e:
                        # For debugging
                        if success_count < 3:
                            print(f"    [ERROR] Success {success_count}: Ranking extraction completely failed - {e}")
                            import traceback
                            traceback.print_exc()
                    
                    # Debug: Print final ranking info for first 3 products
                    if success_count < 3:
                        print(f"    [DATA] Success {success_count} final: ranking={ranking}, is_ad={is_ad}, store_id={store_id}")
                    
                    # VBA: StoreReviewCount (lines 832-868)
                    review_count = 0
                    
                    # Try multiple selectors
                    review_selectors = [
                        ".adProduct_count__J5x57",
                        ".product_num__WuH26",
                        ".product_etc__Z7jnS em",  # Review count may be in em tag
                        "[class*='product'][class*='num']",  # Contains product and num in class name
                    ]
                    
                    review_found = False
                    for selector in review_selectors:
                        try:
                            review_elem = store.find_element(By.CSS_SELECTOR, selector)
                            review_text = review_elem.text.strip()
                            if success_count < 3:
                                print(f"    [DEBUG] Success {success_count}: Review element found ({selector}) - text='{review_text}'")
                            if review_text:
                                review_count = self._parse_review_count(review_text)
                                if success_count < 3:
                                    print(f"    [OK] Success {success_count}: Review count parsed - {review_count}")
                                review_found = True
                                break
                        except:
                            continue
                    
                    if not review_found:
                        # VBA: If no review count, search in spans
                        if success_count < 3:
                            print(f"    [WARNING] Success {success_count}: Direct selector failed, searching in spans...")
                        try:
                            spans = store.find_elements(By.CSS_SELECTOR, ".product_etc__Z7jnS, .adProduct_review__DQla5, .adProduct_etc__AM_WB")
                            if success_count < 3:
                                print(f"    [DEBUG] Success {success_count}: Found {len(spans)} spans")
                            for span in spans:
                                span_text = span.text.strip()
                                if success_count < 3:
                                    print(f"       - Span text: '{span_text}'")
                                if '리뷰' in span_text:
                                    if '(' in span_text:  # For ads: Rating 5 Review(1)
                                        review_count = self._parse_review_count(span_text.split('(')[1].split(')')[0])
                                    else:
                                        review_count = self._parse_review_count(span_text)
                                    if success_count < 3:
                                        print(f"    [OK] Success {success_count}: Review count extracted from span - {review_count}")
                                    break
                        except Exception as e2:
                            if success_count < 3:
                                print(f"    [ERROR] Success {success_count}: Span search also failed - {e2}")
                    
                    # VBA: StoreLikeCount (lines 839-873)
                    like_count = 0
                    try:
                        spans = store.find_elements(By.CSS_SELECTOR, ".product_etc__Z7jnS, .adProduct_review__DQla5, .adProduct_etc__AM_WB")
                        for span in spans:
                            span_text = span.text.strip()
                            if '찜' in span_text:
                                like_count = self._parse_review_count(span_text.replace('찜', ''))
                                break
                    except:
                        pass
                    
                    # VBA: StoreGrade, StoreServiceGrade (lines 875-903)
                    store_grade = ""
                    service_grade = ""
                    try:
                        grade_container = store.find_element(By.CSS_SELECTOR, ".product_mall_area__32KR3, .adProduct_mall_area__XKm_G")
                        grade_elems = grade_container.find_elements(By.CSS_SELECTOR, ".product_grade__O_5f5, .adProduct_grade__wZiUX")
                        
                        for i, grade_elem in enumerate(grade_elems):
                            grade_text = grade_elem.text.strip()
                            if grade_text:
                                if grade_text == "굿서비스":
                                    service_grade = grade_text
                                elif not store_grade:
                                    store_grade = grade_text
                                elif not service_grade:
                                    service_grade = grade_text
                    except:
                        pass
                    
                    # Debug: Final nv_mid check before saving
                    if success_count < 3:
                        print(f"    [SAVE] Success {success_count}: Before save nv_mid={nv_mid}, price={price}")
                    
                    # Save result (VBA column names + Extension ranking) - Disabled
                    # results.append({
                    #     'ProductName': product_name,        # VBA: ProductName
                    #     'Name': mall_name,             # VBA: Name (StoreName)
                    #     'StoreId': store_id,       # VBA: StoreId
                    #     'url': f'https://brand.naver.com/{store_id}' if is_brand else f'https://smartstore.naver.com/{store_id}',  # VBA: url
                    #     'ProductUrl': product_url,        # Product link
                    #     'nv_mid': nv_mid,             # Product unique ID
                    #     'Price': price,                 # Product price
                    #     'Store': 'Brand' if is_brand else '',  # VBA: Store (brand status)
                    #     'ReviewCount': review_count,         # VBA: ReviewCount
                    #     'LikeCount': like_count,             # VBA: LikeCount
                    #     'Grade': store_grade,           # VBA: Grade
                    #     'Service': service_grade,        # VBA: Service
                    #     'ranking': ranking,            # Extension: Search ranking
                    #     'Ad': 'Ad' if is_ad else '',  # Extension: Ad status
                    #     'TalkTalkId': talk_id,          # TalkTalk ID
                    #     'TalkTalkUrl': f'https://talk.naver.com/ct/{talk_id}' if talk_id else '',  # VBA: TalkTalkUrl
                    # })
                    
                    success_count += 1  # Increment success counter
                    
                    if (idx + 1) % 10 == 0:
                        print(f"  [DATA] Progress: {idx + 1}/{len(store_elements)} processed, {len(results)} extracted")
                
                except Exception as e:
                    # Ignore individual product processing failures and continue
                    continue
            
            print(f"  [OK] Step 1 complete: {len(results)} SmartStores")
            return results
        
        except Exception as e:
            print(f"  [WARNING] Data extraction error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_review_count(self, text):
        """
        VBA function: ProcessReviewOnly (lines 1600-1614)
        Parse review/like count ("1,234" -> 1234, "1.2만" -> 12000)
        """
        if not text:
            return 0
        
        # VBA: CurrentReviewCount = Replace(CurrentReviewCount, " ", "")
        text = text.replace(' ', '')
        text = text.replace('리뷰', '')
        text = text.replace('(', '')
        text = text.replace(')', '')
        text = text.replace(',', '')
        
        if not text:
            return 0
        
        # VBA: If InStr(CurrentReviewCount, "만") <> 0 Then
        if '만' in text:
            try:
                number = text.replace('만', '')
                return int(float(number) * 10000)
            except:
                return 0
        else:
            try:
                return int(text)
            except:
                return 0
    
    def _get_store_info_from_api(self, store_id):
        """
        Query store info from API(DB) (VBA: getDataDB function)
        VBA: lines 2277-2307
        
        Returns:
            dict or None: Store info on success, None on failure
        """
        try:
            import requests
            
            url = f"https://api.mgunexcel.com/getssseller?id={store_id}"
            response = requests.get(url, timeout=5)
            
            # VBA: If InStr(res, "|") = 0 Then Exit Sub
            if "Internal Server Error" in response.text or "|" not in response.text:
                return None
            
            # VBA: resArr = Split(res, "|||")
            data = response.text.strip('"').split("|||")
            
            # VBA column order (lines 2289-2290: Resize(1, 18))
            # StoreId(1) + BusinessName(2) + StoreDescription(3) + ... total 18
            # API response: 0=keyword, 1=StoreID, 2=BusinessName, 3=empty, 4=CEO, ...
            
            # VBA: If value = "None" Then value = ""
            def get_value(idx):
                if idx < len(data):
                    val = data[idx].strip()
                    return "" if val in ["None", ""] else val
                return ""
            
            # Contact handling (VBA: CellPhone + Contact)
            # Index 5: Cell phone (010-xxxx-xxxx)
            # Index 6: Landline (064-xxxx-xxxx)
            cell_phone = get_value(5)  # Cell phone
            just_phone = get_value(6)  # Contact (landline)
            
            # Use either one if available (VBA: Cell phone priority)
            contact = cell_phone if cell_phone else just_phone
            
            # Return with VBA column names
            return {
                'BusinessName': get_value(2),              # VBA: BusinessName
                'CEO': get_value(4),              # VBA: CEO
                'Contact': contact,                   # VBA: Contact (cell or landline)
                'Email': get_value(7),              # VBA: Email
                'BusinessNumber': get_value(8),       # VBA: BusinessNumber
                'BusinessAddress': get_value(9),         # VBA: BusinessAddress
                'EcommerceNumber': get_value(10),      # VBA: EcommerceNumber
            }
        
        except Exception as e:
            print(f"    [WARNING] API query failed: {e}")
            return None
    
    def _extract_detailed_info_by_crawling(self, store_id, is_brand=False):
        """
        Crawl detailed info from store profile page (VBA: commented code lines 1268-1329)
        Warning: Not actually used in VBA (all commented out)
        """
        try:
            # VBA: If list.ListColumns("Store").DataBodyRange(row) = "Brand" Then
            if is_brand:
                profile_url = f"https://brand.naver.com/{store_id}/profile?cp=1"
            else:
                profile_url = f"https://smartstore.naver.com/{store_id}/profile?cp=1"
            
            print(f"    [SEARCH] Extracting detailed info for {store_id} by crawling...")
            self.driver.get(profile_url)
            time.sleep(random.uniform(1.0, 1.5))
            
            # Important: Click "View Details" button -> Popup window opens
            # Must click button on profile page to display seller info
            # Popup: https://shopping.naver.com/popup/seller-info/{hash}/profile?...
            original_window = self.driver.current_window_handle
            
            try:
                # Try multiple selectors to find button
                detail_button = None
                button_selectors = [
                    "//button[contains(text(), '상세 정보 확인')]",
                    "//button[contains(text(), '상세정보')]",
                    "//a[contains(text(), '상세 정보 확인')]",
                    "//a[contains(text(), '상세정보')]",
                    "//div[contains(@class, 'detail')]//button",
                    "//button[contains(@class, 'detail')]"
                ]
                
                for selector in button_selectors:
                    try:
                        detail_button = self.driver.find_element(By.XPATH, selector)
                        if detail_button:
                            print(f"    [BUTTON] Clicking 'View Details' button...")
                            detail_button.click()
                            time.sleep(2.0)  # Wait for popup to open
                            break
                    except:
                        continue
                
                # Switch to popup window
                all_windows = self.driver.window_handles
                if len(all_windows) > 1:
                    # Switch to new popup window
                    for window in all_windows:
                        if window != original_window:
                            self.driver.switch_to.window(window)
                            print(f"    [WINDOW] Switched to popup window")
                            break
                    
                    # Wait 3 seconds (time for user to solve captcha + page loading)
                    print(f"    [WAIT] Waiting for page loading (3 seconds)...")
                    time.sleep(3)
                    
                    time.sleep(1.0)  # Additional stabilization wait
                else:
                    print(f"    [WARNING] Popup did not open, attempting to extract info from current page")
            
            except Exception as e:
                print(f"    [WARNING] Button click failed: {e}")
            
            # VBA: Set InfoObject = SEL.FindElementsByClass("_1kgEGGOBTi")
            # Extract info from popup window
            
            # Debug: Print part of page source
            try:
                page_source = self.driver.page_source
                if "상호명" in page_source:
                    print(f"    [OK] 'BusinessName' text exists in page")
                    # Extract HTML around business name
                    idx = page_source.find("상호명")
                    snippet = page_source[max(0, idx-200):min(len(page_source), idx+200)]
                    print(f"    [PAGE] HTML snippet: {snippet[:100]}...")
                else:
                    print(f"    [WARNING] 'BusinessName' text not found in page")
            except Exception as e:
                print(f"    [WARNING] Page source check failed: {e}")
            
            info_elements = self.driver.find_elements(By.CLASS_NAME, "_1kgEGGOBTi")
            print(f"    [NOTE] Extractable info items: {len(info_elements)}")
            
            # Initialize info to extract
            business_name = ""  # Business name
            ceo_name = ""       # CEO
            contact = ""        # Contact
            business_number = "" # Business registration number
            address = ""        # Business address
            ecommerce_number = "" # E-commerce registration number
            email = ""          # Email
            
            # VBA: For Each Object In InfoObjects
            for i, element in enumerate(info_elements):
                try:
                    # VBA: Select Case Object.FindElementsByClass("_2E256BP8nc")(1).Text
                    label_elem = element.find_elements(By.CLASS_NAME, "_2E256BP8nc")
                    value_elem = element.find_elements(By.CLASS_NAME, "_2PXb_kpdRh")
                    
                    if not label_elem or not value_elem:
                        continue
                    
                    label = label_elem[0].text.strip()
                    value = value_elem[0].text.strip()
                    
                    # Debug: Print extracted info
                    print(f"      [{i+1}] {label}: {value[:30]}..." if len(value) > 30 else f"      [{i+1}] {label}: {value}")
                    
                    # VBA Select Case logic
                    if label == "상호명":
                        business_name = value
                    elif label == "대표자":
                        # VBA: CEO = Split(CEO, ",")(0)
                        ceo_name = value.split(',')[0].split('(')[0].strip()
                    elif label == "고객센터":
                        # VBA: Contact = Replace(Contact, "Verified", "")
                        contact = value.replace("인증", "").replace("잘못된 번호 신고", "").strip()
                    elif label == "사업자등록번호":
                        business_number = value
                    elif label == "사업장 소재지":
                        address = value
                    elif label == "통신판매업번호":
                        ecommerce_number = value
                    elif label == "e-mail":
                        email = value
                
                except Exception as e:
                    print(f"      [WARNING] [{i+1}] Extraction error: {e}")
                    continue
            
            # Extraction result summary
            print(f"    [OK] Extraction complete: BusinessName={business_name}, CEO={ceo_name}, Contact={contact}")
            
            # Return with VBA column names
            result = {
                'BusinessName': business_name,
                'CEO': ceo_name,
                'Contact': contact,
                'BusinessNumber': business_number,
                'BusinessAddress': address,
                'EcommerceNumber': ecommerce_number,
                'Email': email,
            }
            
            # Close popup window and return to original window
            try:
                all_windows = self.driver.window_handles
                if len(all_windows) > 1:
                    # Close current popup window
                    self.driver.close()
                    # Switch to original window
                    self.driver.switch_to.window(original_window)
                    print(f"    [BACK] Returned to original window")
            except:
                pass
            
            return result
        
        except Exception as e:
            print(f"    [WARNING] Crawling failed: {e}")
            
            # Try to return to original window even on error
            try:
                all_windows = self.driver.window_handles
                if len(all_windows) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
            except:
                pass
            
            return {}
    
    def crawl_multiple_keywords(self, keywords, pages_per_keyword=5, domestic=True, extract_detailed=False):
        """
        Crawl multiple keywords (VBA method: extract detailed info immediately after each store extraction)
        
        Args:
            keywords: Keyword list
            pages_per_keyword: Pages to crawl per keyword
            domestic: True=Domestic, False=International
            extract_detailed: If True, extract detailed info (business info) for each store (VBA: FillStoreInfo)
        
        Returns:
            DataFrame: Crawling results
        """
        all_data = []
        total = len(keywords) * pages_per_keyword
        current = 0
        
        # Track already processed store IDs (VBA: already loaded store check)
        processed_stores = set()
        
        for keyword_idx, keyword in enumerate(keywords):
            if not keyword.strip():
                continue
                
            print(f"\n{'='*60}")
            print(f"[BOX] Keyword: {keyword}")
            print(f"{'='*60}")
            
            for page in range(1, pages_per_keyword + 1):
                current += 1
                print(f"[{current}/{total}] Crawling...")
                
                try:
                    # Use natural search for first page of each keyword
                    first_search = (page == 1)
                    
                    data = self.crawl_page(
                        keyword=keyword, 
                        page=page,
                        domestic=domestic,
                        first_search=first_search
                    )
                    
                    # VBA method: Extract detailed info immediately after each store extraction
                    for item in data:
                        store_id = item['StoreId']
                        
                        # VBA: If IdDict.Exists(StoreId) = False Then
                        if store_id in processed_stores:
                            print(f"  [SKIP] Already processed store: {store_id}")
                            continue
                        
                        # Add keyword info (VBA column names)
                        item['Keyword'] = keyword  # VBA: Keyword
                        item['Page'] = page      # VBA: Page
                        
                        # VBA: Call FillStoreInfoActual(list.ListRows.Count)
                        # VBA also only uses API (getDataDB)
                        if extract_detailed:
                            print(f"  [SEARCH] Extracting detailed info for {store_id}...")
                            
                            # Query detailed info from API (VBA: Call getDataDB)
                            detailed_info = self._get_store_info_from_api(store_id)
                            if detailed_info and detailed_info.get('BusinessName'):
                                print(f"    [OK] API query succeeded!")
                                item.update(detailed_info)
                            else:
                                print(f"    [WARNING] No info in API")
                            
                            # VBA: d.start 1000 * formSearch.inputDelay (delay time)
                            time.sleep(random.uniform(1.0, 1.5))
                        
                        all_data.append(item)
                        processed_stores.add(store_id)
                    
                    print(f"  [DATA] Cumulative: {len(all_data)} (duplicates excluded)")
                    
                except Exception as e:
                    print(f"  [ERROR] Error: {e}")
                    continue
        
        # Create DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            print(f"\n[OK] Total {len(df)} stores collected!")
            return df
        else:
            return pd.DataFrame()
    
    def wait_for_login(self, timeout=300):
        """
        Wait for user to login manually
        Natural method like VBA original
        
        Args:
            timeout: Maximum wait time (seconds)
        
        Returns:
            bool: Login success status
        """
        print("\n" + "="*60)
        print("[LOCK] Naver Login")
        print("="*60)
        print("[PIN] Please complete Naver login in the browser.")
        print(f"[TIME] Waiting up to {timeout} seconds...")
        print("="*60)
        
        # 1. Navigate to Naver main page (naturally)
        print("\n[HOME] Navigating to Naver main page...")
        self.driver.get("https://www.naver.com")
        self.chrome.human_delay(2, 3)  # 1~2 sec -> 2~3 sec (wait for page loading)
        
        # 2. Find and click login button
        try:
            print("[SEARCH] Finding login button...")
            
            # Wait for page loading
            time.sleep(1)
            
            # Login button selectors
            login_selectors = [
                ".link_login",
                "a[href*='nid.naver.com']",
                ".area_links a.link_login"
            ]
            
            login_btn = None
            # Try max 5 times (5 seconds)
            for attempt in range(5):
                for selector in login_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            # Check if element is visible on screen
                            if elem.is_displayed():
                                text = elem.text.strip()
                                href = elem.get_attribute('href') or ''
                                if '로그인' in text or 'login' in href.lower():
                                    login_btn = elem
                                    break
                        if login_btn:
                            break
                    except:
                        continue
                
                if login_btn:
                    break
                    
                # Wait 1 second and retry if not found
                if attempt < 4:
                    print(f"  [WAIT] Finding login button... (attempt {attempt + 1}/5)")
                    time.sleep(1)
            
            if login_btn:
                print("[OK] Login button found! Clicking...")
                
                # Simple click like VBA
                try:
                    login_btn.click()
                    self.chrome.human_delay(2, 3)
                except Exception as e:
                    # Navigate directly on click failure
                    print(f"[WARNING] Login button click failed: {e}, navigating directly...")
                    self.driver.get("https://nid.naver.com/nidlogin.login")
                    self.chrome.human_delay(2, 3)
            else:
                # Navigate directly if login button not found
                print("[WARNING] Login button not found, navigating directly...")
                self.driver.get("https://nid.naver.com/nidlogin.login")
                self.chrome.human_delay(1, 2)
        
        except Exception as e:
            print(f"[WARNING] Login button click failed: {e}")
            self.driver.get("https://nid.naver.com/nidlogin.login")
            self.chrome.human_delay(1, 2)
        
        # 3. Wait for login completion
        print("\n[WAIT] Please complete login...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check login completion
            current_url = self.driver.current_url
            
            # Check if left nid.naver.com
            if "nid.naver.com" not in current_url:
                # Login complete if no login button (no refresh!)
                try:
                    login_elements = self.driver.find_elements(By.CSS_SELECTOR, ".link_login")
                    if not login_elements:
                        print("\n[OK] Login complete!")
                        # Remove unnecessary main page navigation
                        self.chrome.human_delay(1, 2)
                        return True
                except:
                    # Success if left nid even if login button search fails
                    print("\n[OK] Login complete!")
                    self.chrome.human_delay(1, 2)
                    return True
            
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            print(f"\r[WAIT] Waiting for login... ({elapsed} seconds elapsed / {remaining} seconds remaining)", end="", flush=True)
            
            time.sleep(2)
        
        print("\n[ERROR] Login timeout")
        return False
