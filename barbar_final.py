import os
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- AYARLAR ---
HEDEF_PROFIL_URL = "https://www.instagram.com/eceerken/" 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if os.path.dirname(os.path.abspath(__file__)) else os.getcwd()
KLASOR_ADI = os.path.join(SCRIPT_DIR, "eceerken_hasat")
MAX_POST_SAYISI = 50

def barbar_v4_network_hunter():
    print("-" * 50)
    print("☠️  BARBAR VİTRİN v4.0 (NETWORK HUNTER)")
    print("-" * 50)
    print("ÖZELLİK: Network trafiğinden gerçek video URL yakalama")

    # Klasör oluştur
    try:
        if not os.path.exists(KLASOR_ADI):
            os.makedirs(KLASOR_ADI)
            print(f"✅ Klasör oluşturuldu: {KLASOR_ADI}")
        else:
            print(f"✅ Klasör mevcut: {KLASOR_ADI}")
    except Exception as e:
        print(f"❌ Klasör oluşturulamadı: {e}")
        return

    print("\n🔧 Chrome hazırlanıyor...")
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3") 
    options.add_argument("--mute-audio")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Performance log'u aktifleştir (Network trafiği için)
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.instagram.com/")
        print("\n" + "="*60)
        print("🚨 GÖREV ZAMANI:")
        print("1. Instagram'a GİRİŞ YAP.")
        print("2. 'Şifre Kaydedilsin mi?' -> 'Şimdi Değil'.")
        print(f"3. Hedef profile git: {HEDEF_PROFIL_URL}")
        print("4. Sayfayı SONUNA KADAR SCROLL et (lazy load için)")
        print("5. Buraya dön ve ENTER'a bas.")
        print("="*60 + "\n")
        input("👉 Hazır mısın? Enter'a bas...")

        # --- SELECTOR TESTİ ---
        print("\n🔍 Selector testleri yapılıyor...")
        
        selectors = [
            "article a[href*='/p/']",
            "a[href*='/p/']",
            "a[href*='/reel/']",
            "main a",
            "div._ac7v a",
        ]
        
        best_selector = None
        best_count = 0
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"   📌 '{selector}' → {len(elements)} element")
                if len(elements) > best_count:
                    best_count = len(elements)
                    best_selector = selector
            except Exception as e:
                print(f"   ❌ '{selector}' → HATA")
        
        if best_count == 0:
            print("\n❌ KRİTİK: Hiçbir selector çalışmadı!")
            input("\nSayfayı scroll edip Enter'a bas...")
            return
        
        print(f"\n✅ En iyi selector: '{best_selector}' ({best_count} post)")
        
        # Session Hazırlığı
        cookies = driver.get_cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        session.headers.update({'User-Agent': driver.execute_script("return navigator.userAgent;")})

        unique_media = set()
        processed_posts = 0
        scroll_attempts = 0
        max_scroll = 10
        
        while True:
            # POST TOPLA
            try:
                post_links = driver.find_elements(By.CSS_SELECTOR, best_selector)
                
                filtered_links = []
                for link in post_links:
                    href = link.get_attribute('href')
                    if href and ('/p/' in href or '/reel/' in href):
                        filtered_links.append(link)
                
                post_links = filtered_links
                
            except Exception as e:
                print(f"❌ Post toplama hatası: {e}")
                post_links = []
            
            print(f"\n📊 Grid'de {len(post_links)} post, {processed_posts} işlendi.")
            
            # YENİ POSTLARI İŞLE
            new_posts_found = False
            
            for i in range(len(post_links)):
                try:
                    # Elementi yeniden bul (Stale Element önlemi)
                    current_links = driver.find_elements(By.CSS_SELECTOR, best_selector)
                    filtered = [l for l in current_links if l.get_attribute('href') and 
                               ('/p/' in l.get_attribute('href') or '/reel/' in l.get_attribute('href'))]
                    
                    if i >= len(filtered):
                        continue
                    
                    post_link = filtered[i]
                    post_url = post_link.get_attribute('href')
                    
                    if not post_url or post_url in unique_media:
                        continue
                    
                    new_posts_found = True
                    unique_media.add(post_url)
                    
                    print(f"\n🎯 Post {processed_posts + 1}/{MAX_POST_SAYISI or '∞'}")
                    print(f"   URL: {post_url}")
                    
                    # Performance log'u temizle
                    driver.get_log('performance')
                    
                    # TIKLAMA
                    driver.execute_script("arguments[0].scrollIntoView(true);", post_link)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", post_link)
                    time.sleep(3)  # Network isteği için biraz daha bekle
                    
                    # MEDYA YAKALA (Network trafiği ile)
                    extract_media_from_modal_v2(driver, session)
                    
                    # KAPAT
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(1.5)
                    
                    processed_posts += 1
                    
                    if MAX_POST_SAYISI and processed_posts >= MAX_POST_SAYISI:
                        print(f"\n✅ Hedef sayıya ulaşıldı ({MAX_POST_SAYISI})")
                        return
                    
                except Exception as e:
                    print(f"⚠️ Post işleme hatası: {str(e)[:80]}")
                    try:
                        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                        time.sleep(1)
                    except:
                        pass
            
            # SCROLL
            if not new_posts_found or scroll_attempts < max_scroll:
                print("\n🔄 Scroll yapılıyor...")
                last_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                new_height = driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    scroll_attempts += 1
                    if scroll_attempts >= 3:
                        print("\n✅ Sayfa sonu.")
                        break
                else:
                    scroll_attempts = 0
            else:
                break

    except Exception as e:
        print(f"\n❌ KRİTİK HATA: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print(f"\n{'='*60}")
        print(f"✅ İŞLEM BİTTİ")
        print(f"📦 İşlenen Post: {processed_posts}")
        print(f"📂 Klasör: {KLASOR_ADI}")
        print(f"{'='*60}")
        if 'driver' in locals():
            driver.quit()
        input("\nKapatmak için Enter...")


def extract_media_from_modal_v2(driver, session):
    """Modal içindeki medyaları çeker - Network trafiği ile video URL yakalama."""
    
    scanned_urls = set()
    carousel_count = 0
    
    # --- NETWORK TRAFİĞİNDEN VİDEO URL YAKALA ---
    video_urls = []
    try:
        logs = driver.get_log('performance')
        for log in logs:
            try:
                message = json.loads(log['message'])
                method = message['message']['method']
                
                # Network isteğini yakala
                if method == 'Network.responseReceived':
                    response = message['message']['params']['response']
                    url = response.get('url', '')
                    
                    # Instagram video URL'leri genelde .mp4 içerir ve cdninstagram.com domain'i kullanır
                    if '.mp4' in url and ('cdninstagram.com' in url or 'fbcdn.net' in url):
                        video_urls.append(url)
                        print(f"   🎬 Network'ten video yakalandı: {url[:60]}...")
            except:
                pass
    except Exception as e:
        print(f"   ⚠️ Network log hatası: {str(e)[:50]}")
    
    # Yakalanan videoları indir
    for video_url in video_urls:
        if video_url not in scanned_urls:
            scanned_urls.add(video_url)
            download_media(session, video_url, "video")
    
    # --- NORMAL MEDYA YAKALAMA (Resimler için) ---
    while True:
        try:
            # RESİMLER
            images = driver.find_elements(By.CSS_SELECTOR, "img")
            for img in images:
                try:
                    width = img.get_attribute('naturalWidth')
                    if width:
                        w = int(width)
                        if w < 300:
                            continue
                    
                    src = img.get_attribute('src')
                    srcset = img.get_attribute('srcset')
                    
                    if srcset:
                        src = srcset.split(',')[-1].strip().split(' ')[0]
                    
                    if src and src.startswith("http") and "base64" not in src:
                        if "/s150x150/" in src or "/s320x320/" in src:
                            continue
                        
                        if src not in scanned_urls:
                            print(f"   🖼️ Resim: {src[:50]}...")
                            scanned_urls.add(src)
                            download_media(session, src, "image")
                except:
                    pass
            
            # CAROUSEL NEXT
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, 
                    "button[aria-label='Next'], button[aria-label='İleri'], button[aria-label='Sonraki']")
                
                driver.execute_script("arguments[0].click();", next_btn)
                carousel_count += 1
                print(f"   ↪️ Carousel {carousel_count + 1}")
                time.sleep(1.5)
            except:
                if carousel_count > 0:
                    print(f"   ✅ Carousel bitti ({carousel_count + 1} sayfa)")
                break
                
        except Exception as e:
            print(f"   ⚠️ Modal hata: {str(e)[:50]}")
            break


def download_media(session, url, media_type):
    """Medyayı indirir."""
    try:
        # Klasör kontrolü
        if not os.path.exists(KLASOR_ADI):
            os.makedirs(KLASOR_ADI)
        
        ext = "mp4" if media_type == "video" else "jpg"
        
        if ".mp4" in url:
            ext = "mp4"
        elif ".jpg" in url or ".jpeg" in url:
            ext = "jpg"
        elif ".png" in url:
            ext = "png"
        
        # Dosya adını güvenli hale getir
        safe_filename = f"{media_type}_{int(time.time()*10000)}.{ext}"
        filename = os.path.join(KLASOR_ADI, safe_filename)
        
        r = session.get(url, stream=True, timeout=15)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            print(f"   ✅ İndirildi: {safe_filename}")
        else:
            print(f"   ❌ HTTP {r.status_code}")
            
    except Exception as e:
        print(f"   ❌ İndirme hatası: {str(e)}")


if __name__ == "__main__":
    barbar_v4_network_hunter()