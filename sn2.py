#!/usr/bin/env python3
"""
INSTAGRAM HASHTAG SCRAPER WITH DATA ANALYSIS (2024 WORKING VERSION)
- Handles OTP verification
- Modern 2024 selectors
- Anti-detection measures
- Multiple fallback methods
- Full data analysis
"""

from matplotlib import pyplot as plt
import matplotlib
import warnings
import os
import time
import random
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
# Configure environment to prevent warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)

# Set matplotlib to non-GUI backend
matplotlib.use('Agg')


class InstagramScraper:
    def __init__(self):
        self.driver = self._init_driver()
        self.wait = WebDriverWait(self.driver, 20)

    def _init_driver(self):
        options = webdriver.ChromeOptions()

        # 2024-2025 stealth flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "--disable-features=IsolateOrigins,site-per-process")
        options.add_argument("--disable-site-isolation-trials")
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_argument(
            f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(122,127)}.0.0.0 Safari/537.36")

        # New 2024-2025 required arguments
        options.add_argument("--no-first-run")
        options.add_argument("--no-service-autorun")
        options.add_argument("--no-default-browser-check")

        driver = webdriver.Chrome(options=options)

        # Modern stealth injection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                configurable: true
            });
            window.chrome = { runtime: {} };
            """
        })
        return driver

    def login(self, username, password):
        """Secure login with OTP handling"""
        print("🌐 Logging in to Instagram...")
        self.driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(random.uniform(2, 4))

        # Handle cookie dialog
        try:
            self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Allow essential')]")
            )).click()
        except:
            pass

        # Enter credentials
        username_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, "username")))
        username_field.send_keys(username)

        password_field = self.driver.find_element(By.NAME, "password")
        password_field.send_keys(password + Keys.RETURN)

        time.sleep(3)

        otp_detected = False
        # OTP handling
        try:
            # self.wait.until(EC.presence_of_element_located((By.NAME, "verificationCode")))
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "verificationCode"))
            )
            input("🔑 Enter OTP in browser then press Enter here to continue...")
            otp_detected = True
        except:
            print("No OTP required")

        if otp_detected:
            try:
                WebDriverWait(self.driver, 60).until(
                    EC.url_contains("https://www.instagram.com/")
                )
            except TimeoutException:
                print("OTP verification took too long - proceeding anyway")

        # Dismiss notifications prompt
        try:
            self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Not Now')]")
            )).click()
        except:
            pass

        print("✅ Login successful")

    def scrape_hashtag(self, hashtag, max_posts=10):
        """Scrape posts with modern selectors"""
        print(f"🔍 Scraping #{hashtag}...")
        self.driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
        time.sleep(4)

        posts = set()
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")
        scroll_attempts = 0

        while len(posts) < max_posts and scroll_attempts < 5:
            # Scroll and collect
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(1.5, 3.5))

            # Modern 2024 post detection
            anchors = self.driver.find_elements(
                By.XPATH, "//a[contains(@href, '/p/') or contains(@href, '/reel/')]")
            for a in anchors[:max_posts]:
                href = a.get_attribute("href")
                if href and len(posts) < max_posts:
                    posts.add(href.split("?")[0])  # Remove tracking parameters

            # Check scroll progress
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
            last_height = new_height

        return list(posts)[:max_posts]

    def get_post_details(self, post_url):
        """2024-Compatible post detail extraction with safer JS"""
        try:
            for attempt in range(3):
                try:
                    self.driver.get(post_url)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
                    )
                    break
                except Exception:
                    if attempt == 2:
                        print(f"[ERROR] Failed to load post: {post_url}")
                        return None
                    time.sleep(2)

            # Simplified JavaScript execution
            script = """
            try {
                function getText(selector) {
                    var el = document.querySelector(selector);
                    return el ? el.textContent.trim() : null;
                }

                function extractNumber(text) {
                    var match = text.match(/[\d,.]+/);
                return match ? parseInt(match[0].replace(/,/g, '')) : 0;
                }

            var username = getText('header a[href^="/"]');
                if (!username) {
                    var reelUser = document.querySelector('a[href*="/reels/"]');
                if (reelUser) {
                    username = reelUser.closest('div').previousElementSibling.querySelector('a').textContent.trim();
            }
        }

        var captionEl = document.querySelector('ul > div > li > div > div > div > span');
        var caption = captionEl ? captionEl.textContent.trim() : '';

        var likes = 0;
        var likeElement = document.querySelector('section[aria-label="Like"]');
        if (likeElement) likes = extractNumber(likeElement.textContent);

        if (likes === 0) {
            var viewsElement = document.querySelector('[aria-label*="views"]');
            if (viewsElement) likes = extractNumber(viewsElement.textContent);
        }

        var timestamp = (document.querySelector('time') || {}).dateTime || '';

        return {
            username: username || 'unknown',
            caption: caption || '',
            likes: likes,
            timestamp: timestamp
        };
    } catch (e) {
        return {
            username: 'error',
            caption: '',
            likes: 0,
            timestamp: ''
        };
    }
            """
            data = self.driver.execute_script(script)

            return {
            'username': data.get('username', 'unknown'),
            'caption': data.get('caption', ''),
            'likes': data.get('likes', 0),
            'timestamp': data.get('timestamp', ''),
            'url': post_url
        }

        except Exception as e:
            print(f"⚠️ Failed to scrape {post_url}: {str(e)}")
            return None

    def analyze_data(self, posts_data, hashtag):
        """Comprehensive data analysis with visualizations"""
        df = pd.DataFrame([p for p in posts_data if p is not None])

        if df.empty:
            print("❌ No valid data collected - Instagram may have blocked you")
            return None

        # Basic stats
        print(f"\n📊 Analysis for #{hashtag}")
        print(f"Total posts: {len(df)}")
        print(
            f"Avg likes: {df['likes'].mean():.0f}" if not df.empty else "No data")
        print(
            f"Top user: {df['username'].mode()[0] if not df['username'].empty else 'N/A'}")

        # Generate visualizations
        self._generate_visuals(df, hashtag)

        # Save data
        df.to_csv(f"{hashtag}_posts.csv", index=False)
        print(f"💾 Data saved to {hashtag}_posts.csv")

        return df

    def _generate_visuals(self, df, hashtag):
        """Create analysis visuals"""
        plt.figure(figsize=(15, 10))

        # Engagement distribution
        plt.subplot(2, 2, 1)
        df['likes'].plot(kind='hist', bins=15, color='skyblue')
        plt.title('Likes Distribution')

        # Top users
        plt.subplot(2, 2, 2)
        df['username'].value_counts().head(5).plot(kind='bar', color='salmon')
        plt.title('Top Posters')

        # Word cloud (if captions exist)
        if not df['caption'].empty:
            from wordcloud import WordCloud
            text = ' '.join(df['caption'].dropna())
            if len(text.split()) > 10:
                plt.subplot(2, 2, 3)
                wordcloud = WordCloud(width=800, height=400,
                                      background_color='white',
                                      max_words=100).generate(text)
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.title('Caption Word Cloud')

        # Save visualization
        plt.tight_layout()
        plt.savefig(f"{hashtag}_analysis.png", dpi=300, bbox_inches='tight')
        print(f"🖼️ Analysis saved to {hashtag}_analysis.png")
        plt.close()

    def close(self):
        """Clean up resources"""
        self.driver.quit()


def main():
    # Configuration
    USERNAME = str(input("username: "))
    PASSWORD = str(input("password: ")) 
    HASHTAG = "food"  # Change to your target hashtag

    # Run scraper
    scraper = InstagramScraper()
    try:
        # Step 1: Login
        scraper.login(USERNAME, PASSWORD)

        # Step 2: Scrape post URLs
        post_urls = scraper.scrape_hashtag(HASHTAG, max_posts=3)
        print(f"Found {len(post_urls)} posts to analyze")

        # Step 3: Collect detailed data
        print("\n📥 Collecting post details...")
        posts_data = []
        for url in post_urls:
            print(f"Scraping: {url}")
            data = scraper.get_post_details(url)
            if data:  # Only append if successful
                posts_data.append(data)
            time.sleep(random.uniform(1, 3))  # Avoid detection

        # Step 4: Analyze results
        scraper.analyze_data(posts_data, HASHTAG)

    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
    finally:
        scraper.close()


if __name__ == "__main__":
    # Verify dependencies
    try:
        import numpy as np
        assert np.__version__.startswith(
            '1.24'), "Please install numpy==1.24.3"
        main()
    except Exception as e:
        print(f"⚠️ Setup error: {str(e)}")
        print("Recommended: pip install numpy==1.24.3 pandas matplotlib selenium bs4 webdriver-manager selenium-stealth")
