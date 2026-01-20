import os
import time
import requests
import yt_dlp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- AYARLAR ---
HEDEF_PROFIL_URL = "https://www.instagram.com/eceerken/" 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if os.path.dirname(os.path.abspath(__file__)) else os.getcwd()
KLASOR_ADI = os.path.join(SCRIPT_DIR, "eceerken_hasat")
MAX_POST_SAYISI = 50

def barbar_v9_hybrid():
    print("-" * 50)
    print("☠️  BARBAR v9.0 (HİBRİT: YT-DLP + SELENIUM)")
    print("-" * 50)
    print("Strateji: Video için yt-dlp, başarısızsa Selenium yedek.")

    if not os.path.exists(KLASOR_ADI):
        os.makedirs(KLASOR_ADI)

    print("\n🔧 Chrome hazırlanıyor...")
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3") 
    options.add_argument("--mute-audio")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.instagram.com/")
        print("\n" + "="*60)
        print("🚨 GÖREV:")
        print("1. GİRİŞ YAP")
        print(f"2. Profile git: {HEDEF_PROFIL_URL}")
        print("3. Scroll et")
        print("4. ENTER'a bas")
        print("="*60 + "\n")
        input("👉 Enter...")

        # Cookie hazırla
        print("\n🍪 Cookie transfer...")
        cookies = driver.get_cookies()
        cookie_file = os.path.join(SCRIPT_DIR, "temp_cookies.txt")
        
        with open(cookie_file, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            for cookie in cookies:
                domain = cookie.get('domain', '')
                flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                path = cookie.get('path', '/')
                secure = 'TRUE' if cookie.get('secure') else 'FALSE'
                expiry = str(int(cookie.get('expiry', time.time() + 3600)))
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
        
        # Session (Selenium yedek için)
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        session.headers.update({'User-Agent': driver.execute_script("return navigator.userAgent;")})

        # yt-dlp config
        ydl_opts = {
            'outtmpl': os.path.join(KLASOR_ADI, 'ytdlp_%(id)s.%(ext)s'),
            'cookiefile': cookie_file,
            'format': 'bestvideo+bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,  # Hata yakalayabilmek için False
        }

        processed = set()
        count = 0
        
        while count < MAX_POST_SAYISI:
            # Link topla
            elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/reel/']")
            
            new_links = []
            for el in elements:
                try:
                    url = el.get_attribute('href')
                    if url and url not in processed:
                        if '/p/' in url or '/reel/' in url:
                            new_links.append((el, url))
                except:
                    pass
            
            if not new_links:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                continue

            print(f"\n📊 {len(new_links)} yeni link")

            # Her linki işle
            for element, url in new_links:
                if count >= MAX_POST_SAYISI:
                    break
                if url in processed:
                    continue
                
                processed.add(url)
                count += 1
                
                print(f"\n🎯 [{count}] {url}")
                
                # ÖNCE YT-DLP DENE
                yt_success = False
                if '/reel/' in url:  # Reels için yt-dlp daha başarılı
                    print("   🔥 yt-dlp deneniyor...")
                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])
                        yt_success = True
                        print("   ✅ yt-dlp başarılı")
                        time.sleep(1)
                    except Exception as e:
                        print(f"   ⚠️ yt-dlp başarısız: {str(e)[:50]}")
                
                # YT-DLP BAŞARISIZSA VEYA POST İSE SELENIUM
                if not yt_success:
                    print("   🔧 Selenium yedek devreye giriyor...")
                    try:
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(2)
                        
                        # Medya çek
                        grab_media_selenium(driver, session)
                        
                        # Kapat
                        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                        time.sleep(1)
                    except Exception as e:
                        print(f"   ⚠️ Selenium hatası: {str(e)[:50]}")
                        try:
                            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                        except:
                            pass
            
            if count >= MAX_POST_SAYISI:
                break
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cookie sil
        if os.path.exists(cookie_file):
            try:
                os.remove(cookie_file)
            except:
                pass
        
        print(f"\n{'='*60}")
        print(f"✅ BİTTİ - {count} post")
        print(f"📂 {KLASOR_ADI}")
        print(f"{'='*60}")
        driver.quit()


def grab_media_selenium(driver, session):
    """Selenium ile resim/carousel yakala."""
    seen = set()
    carousel = 0
    
    while True:
        try:
            # Video poster
            videos = driver.find_elements(By.TAG_NAME, "video")
            for v in videos:
                poster = v.get_attribute('poster')
                if poster and poster not in seen:
                    print(f"      📹 Poster")
                    seen.add(poster)
                    save_selenium(session, poster, "poster")
            
            # Resimler
            imgs = driver.find_elements(By.TAG_NAME, "img")
            for img in imgs:
                try:
                    w = img.get_attribute('naturalWidth')
                    if w and int(w) < 300:
                        continue
                    
                    src = img.get_attribute('src')
                    srcset = img.get_attribute('srcset')
                    
                    if srcset:
                        src = srcset.split(',')[-1].strip().split()[0]
                    
                    if src and src.startswith('http') and src not in seen:
                        if '/s150x150/' in src or '/s320x320/' in src:
                            continue
                        print(f"      🖼️ Resim")
                        seen.add(src)
                        save_selenium(session, src, "image")
                except:
                    pass
            
            # Carousel?
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, 
                    "button[aria-label='Next'], button[aria-label='İleri']")
                driver.execute_script("arguments[0].click();", next_btn)
                carousel += 1
                print(f"      ↪️ Carousel {carousel + 1}")
                time.sleep(1.5)
            except:
                break
        except:
            break


def save_selenium(session, url, ftype):
    """Selenium ile indirme."""
    try:
        ext = "mp4" if ftype == "poster" else "jpg"
        if ".jpg" in url or ".jpeg" in url:
            ext = "jpg"
        
        fname = f"sel_{ftype}_{int(time.time()*10000)}.{ext}"
        path = os.path.join(KLASOR_ADI, fname)
        
        r = session.get(url, timeout=15)
        
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)
            
            size = os.path.getsize(path)
            if size < 3000:
                os.remove(path)
            else:
                print(f"      ✅ {size//1024}KB")
    except:
        pass


if __name__ == "__main__":
    barbar_v9_hybrid()