from flask import Flask, request, send_from_directory
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

app = Flask(__name__)

def setup_driver():
    """Configure and return a headless Chrome driver with specific options."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    
    # Set up custom headers
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Add custom headers that can't be set through chrome_options
    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
        'headers': {
            'Referer': 'https://poki.com/'
        }
    })
    
    return driver

@app.route('/')
def serve_index():
    """Serve the index.html file from the current directory."""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

@app.route('/proxy')
def proxy():
    """Handle proxy requests with header spoofing."""
    target_url = request.args.get('url')
    
    if not target_url:
        return 'URL parameter is required.', 400
    
    try:
        driver = setup_driver()
        
        # Navigate to the target URL and wait for the page to load
        driver.get(target_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("tag name", "body"))
        )
        
        # Get the rendered HTML
        content = driver.page_source
        
        # Clean up
        driver.quit()
        
        return content
        
    except Exception as e:
        print(f'Error: {str(e)}')
        return 'Error loading the URL.', 500

if __name__ == '__main__':
    PORT = 3000
    print(f'Server running at http://localhost:{PORT}')
    app.run(port=PORT)
