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

# FFmpeg yolunu script'in yanına sabitliyoruz
FFMPEG_PATH = os.path.join(SCRIPT_DIR, "ffmpeg.exe")

def barbar_v10_leviathan():
    print("-" * 50)
    print("☠️  BARBAR v10 LEVIATHAN (HİBRİT: RESİM + VİDEO + CAROUSEL)")
    print("-" * 50)
    
    # 0. FFmpeg Kontrolü (HAYATİ ÖNEMLİ)
    if not os.path.exists(FFMPEG_PATH):
        print("❌ HATA: 'ffmpeg.exe' bulunamadı!")
        print(f"Lütfen ffmpeg.exe dosyasını şu klasöre koy: {SCRIPT_DIR}")
        print("Aksi halde videolar SESSIZ veya PARÇALI iner.")
        input("Anlaşıldıysa Enter'a bas...")
    else:
        print("✅ FFmpeg motoru hazır.")

    if not os.path.exists(KLASOR_ADI):
        os.makedirs(KLASOR_ADI)

    # 1. Tarayıcı Hazırlığı
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
        print("🚨 GÖREV ZAMANI:")
        print("1. GİRİŞ YAP.")
        print("2. 'Şimdi Değil' de.")
        print(f"3. {HEDEF_PROFIL_URL} adresine git.")
        print("4. Grid yüklenince buraya dön ve ENTER'a bas.")
        print("="*60 + "\n")
        input("👉 Hazır mısın? Enter'a bas...")

        # 2. COOKIE TRANSFERİ (yt-dlp için)
        print("\n🍪 Cookie'ler yt-dlp için kopyalanıyor...")
        cookies = driver.get_cookies()
        cookie_file = os.path.join(SCRIPT_DIR, "leviathan_cookies.txt")
        user_agent = driver.execute_script("return navigator.userAgent;")
        
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

        # Session (Resim indirmek için)
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        session.headers.update({'User-Agent': user_agent})

        # 3. ANA DÖNGÜ (POSTLARI GEZ)
        processed_urls = set()
        count = 0
        
        while count < MAX_POST_SAYISI:
            # Grid'deki linkleri bul
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/reel/']")
            
            # Yeni linkleri filtrele
            targets = []
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and href not in processed_urls:
                        if '/p/' in href or '/reel/' in href:
                            targets.append(link)
                except: pass
            
            if not targets:
                print("🔄 Scroll...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                continue

            # Linkleri işle
            for link_element in targets:
                if count >= MAX_POST_SAYISI: break
                
                try:
                    post_url = link_element.get_attribute('href')
                    if post_url in processed_urls: continue
                    
                    processed_urls.add(post_url)
                    count += 1
                    
                    print(f"\n🎯 [{count}] İşleniyor: {post_url}")

                    # --- YÖNTEM A: VİDEO İSE YT-DLP KULLAN (En Temizi) ---
                    # Linkin içinde /reel/ varsa veya video ikonunu kontrol edebiliriz ama
                    # en garantisi: Önce yt-dlp ile videoyu dene.
                    
                    # Eğer /reel/ ise kesin videodur, direkt yt-dlp'ye ver
                    if '/reel/' in post_url:
                        print("   🎬 Reels tespit edildi -> yt-dlp (FFmpeg) devreye giriyor...")
                        download_video_ytdlp(post_url, cookie_file, user_agent)
                        continue # Resim aramaya gerek yok

                    # Eğer /p/ ise (Post), içinde hem resim hem video olabilir.
                    # Modal açıp içine bakalım.
                    driver.execute_script("arguments[0].scrollIntoView(true);", link_element)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", link_element)
                    time.sleep(2.5) # Modal açılsın

                    # Modal içini tara
                    has_video = False
                    
                    # Carousel Döngüsü (Resimler İçin)
                    scan_carousel_images(driver, session)
                    
                    # Video var mı kontrol et?
                    if len(driver.find_elements(By.CSS_SELECTOR, "video")) > 0:
                        has_video = True
                    
                    # Modal'ı kapat
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(1)

                    # Eğer postun içinde video gördüysek, yt-dlp'yi o URL'e saldırtıyoruz
                    if has_video:
                        print("   📹 Post içinde video görüldü -> yt-dlp indiriyor...")
                        download_video_ytdlp(post_url, cookie_file, user_agent)

                except Exception as e:
                    print(f"⚠️ Hata: {e}")
                    try:
                        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    except: pass

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    except Exception as e:
        print(f"\n❌ GENEL HATA: {e}")

    finally:
        if os.path.exists(cookie_file):
            try: os.remove(cookie_file)
            except: pass
        print(f"\n✅ İŞLEM BİTTİ. Dosyalar: {KLASOR_ADI}")
        input("Kapatmak için Enter...")
        driver.quit()

def scan_carousel_images(driver, session):
    """Modal içindeki resimleri (Carousel dahil) Selenium ile indirir."""
    scanned_srcs = set()
    carousel_page = 0
    
    while True:
        # Resimleri Bul
        images = driver.find_elements(By.CSS_SELECTOR, "article img")
        for img in images:
            try:
                # Boyut kontrolü (ikonları ele)
                w = img.get_attribute('naturalWidth')
                if w and int(w) < 300: continue
                
                # En yüksek kaliteyi al
                src = img.get_attribute('src')
                srcset = img.get_attribute('srcset')
                if srcset: src = srcset.split(',')[-1].strip().split(' ')[0]
                
                if src and src.startswith('http') and src not in scanned_srcs:
                    scanned_srcs.add(src)
                    print(f"   🖼️ Resim bulundu: {src[:40]}...")
                    download_image(session, src)
            except: pass
            
        # Sonraki butonu (Carousel)
        try:
            next_btns = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Next'], button[aria-label='İleri'], button[aria-label='Sonraki']")
            if not next_btns: break
            
            # Görünür olan butona tıkla
            clicked = False
            for btn in next_btns:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                    time.sleep(1.5) # Kayma animasyonu bekle
                    carousel_page += 1
                    break
            
            if not clicked: break # Buton var ama görünür değilse bitmiştir
            
            if carousel_page > 10: break # Sonsuz döngü koruması
            
        except: break

def download_video_ytdlp(url, cookie_file, user_agent):
    """yt-dlp kullanarak videoyu (veya carousel videolarını) indirir."""
    ydl_opts = {
        'outtmpl': os.path.join(KLASOR_ADI, '%(upload_date)s_vid_%(id)s.%(ext)s'),
        'cookiefile': cookie_file,
        'user_agent': user_agent,
        'format': 'bestvideo+bestaudio/best', # En iyi kalite
        'merge_output_format': 'mp4', # MP4 olarak birleştir
        'noplaylist': False, # Carousel ise hepsini indir!
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'ffmpeg_location': FFMPEG_PATH if os.path.exists(FFMPEG_PATH) else None
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"   ❌ yt-dlp hatası: {e}")

def download_image(session, url):
    try:
        fname = f"img_{int(time.time()*10000)}.jpg"
        path = os.path.join(KLASOR_ADI, fname)
        r = session.get(url, timeout=10)
        if r.status_code == 200:
            with open(path, 'wb') as f: f.write(r.content)
    except: pass

if __name__ == "__main__":
    barbar_v10_leviathan()