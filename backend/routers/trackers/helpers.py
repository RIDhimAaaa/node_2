import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re
from urllib.parse import urlparse, urljoin

# Set up logging
logger = logging.getLogger(__name__)

# --- Universal Web Scraper Engine ---

def scrape_website(target_url: str, selector_or_pattern: str = None, search_term: str = None) -> str:
    """
    Universal web scraper that can scrape any website.
    
    Args:
        target_url: The URL to scrape
        selector_or_pattern: CSS selector or regex pattern to find content
        search_term: Term to search for on the page
    
    Returns:
        Scraped content or status message
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    logger.info(f"� [{timestamp}] Universal Scraper: Starting scrape for {target_url}")
    print(f"� [{timestamp}] Universal Scraper: Starting scrape for {target_url}")
    
    # --- DEMO MODES FOR TESTING ---
    if "DEMO123" in search_term:
        import random
        statuses = [
            "Result Pending",
            "Pass - SGPA: 8.75", 
            "Pass - SGPA: 9.25",
            "Result Under Review",
            "Pass - SGPA: 8.90",
            "Application Approved",
            "Document Verification Required"
        ]
        demo_status = random.choice(statuses)
        logger.info(f"🎲 DEMO MODE: Returning random status: {demo_status}")
        print(f"🎲 DEMO MODE: Returning random status: {demo_status}")
        return demo_status
    
    if "12345DEMO" in search_term:
        logger.info("🎭 DEMO MODE: Returning fake successful result.")
        print("🎭 DEMO MODE: Returning fake successful result.")
        return "Pass - SGPA: 9.25"
    # --- END DEMO MODES ---
    
    try:
        # Handle different URL patterns and form submissions
        if "gndu" in target_url.lower():
            return _scrape_gndu_specific(target_url, search_term)
        else:
            return _scrape_generic_website(target_url, selector_or_pattern, search_term)
            
    except Exception as e:
        error_msg = f"Error scraping {target_url}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        print(f"❌ {error_msg}")
        return f"Error: {str(e)}"

def _scrape_gndu_specific(target_url: str, roll_number: str) -> str:
    """Specialized scraper for GNDU website with form submission."""
    try:
        form_payload = {
            'ddlYear': '2025', 'ddlMonth': 'May', 'ddlSem': '4',
            'ddlCourseType': 'CBES', 'ddlCourse': '1702',
            'txtRollNo': roll_number, 'btnSubmit': 'Submit'
        }
        
        response = requests.post(target_url, data=form_payload, timeout=20)
        response.raise_for_status()
        logger.info(f"✅ GNDU response received: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for result span
        result_span = soup.find('span', {'id': 'lblSGPA'})
        if result_span and result_span.text:
            result = f"Pass - SGPA: {result_span.text.strip()}"
            logger.info(f"🎯 GNDU result found: {result}")
            return result
        
        # Look for error message
        error_span = soup.find('span', {'id': 'lblMsg'})
        if error_span and error_span.text:
            error_msg = error_span.text.strip()
            logger.warning(f"⚠️ GNDU error: {error_msg}")
            return error_msg
            
        return "No result found on GNDU page"
        
    except Exception as e:
        return f"GNDU scraping error: {str(e)}"

def _scrape_generic_website(target_url: str, selector_or_pattern: str, search_term: str) -> str:
    """Generic website scraper that works with any URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(target_url, headers=headers, timeout=20)
        response.raise_for_status()
        logger.info(f"✅ Website response received: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # If selector is provided, use it
        if selector_or_pattern:
            if selector_or_pattern.startswith('regex:'):
                # Use regex pattern
                pattern = selector_or_pattern[6:]  # Remove 'regex:' prefix
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                if matches:
                    result = f"Found: {matches[0]}"
                    logger.info(f"🎯 Regex match found: {result}")
                    return result
                else:
                    return "No regex matches found"
            else:
                # Use CSS selector
                elements = soup.select(selector_or_pattern)
                if elements:
                    content = elements[0].get_text(strip=True)
                    result = f"Content: {content[:100]}..." if len(content) > 100 else f"Content: {content}"
                    logger.info(f"🎯 CSS selector match: {result}")
                    return result
                else:
                    return "No elements found with given selector"
        
        # If no selector, search for the term in page text
        if search_term:
            page_text = soup.get_text().lower()
            if search_term.lower() in page_text:
                # Try to find surrounding context
                lines = soup.get_text().split('\n')
                for line in lines:
                    if search_term.lower() in line.lower():
                        result = f"Found: {line.strip()[:150]}..."
                        logger.info(f"🎯 Search term found: {result}")
                        return result
                return f"Term '{search_term}' found on page"
            else:
                return f"Term '{search_term}' not found on page"
        
        # Fallback: return page title and first paragraph
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else "No title"
        
        first_p = soup.find('p')
        p_text = first_p.get_text(strip=True)[:100] if first_p else "No content"
        
        return f"Page: {title_text} | Content: {p_text}..."
        
    except Exception as e:
        return f"Generic scraping error: {str(e)}"

# --- Main Platform Engine ---

def run_scrape_task(target_url: str, selector_or_pattern: str = None, search_term: str = None) -> str:
    """
    Universal scraping engine that can handle any website.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    logger.info(f"🚀 [{timestamp}] Universal Platform: Starting scrape")
    print(f"🚀 [{timestamp}] Universal Platform: Starting scrape")
    print(f"   URL: {target_url}")
    print(f"   Selector: {selector_or_pattern}")
    print(f"   Search Term: {search_term}")
    
    result = scrape_website(target_url, selector_or_pattern, search_term)
    
    logger.info(f"✅ [{timestamp}] Universal Platform: Scrape completed")
    print(f"✅ [{timestamp}] Universal Platform: Scrape completed")
    print(f"   Result: {result}")
    
    return result

# Legacy function for backward compatibility
def scrape_gndu_result(roll_no: str) -> str:
    """Legacy function - redirects to universal scraper"""
    gndu_url = "http://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx"
    return run_scrape_task(gndu_url, None, roll_no)

# New adapter function for URL-based scraping
def universal_scrape(target_url: str, search_term: str) -> str:
    """
    Adapter function that bridges URL-based calls to the universal scraper.
    """
    return run_scrape_task(target_url, None, search_term)
