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

def barbar_v8_nuclear():
    print("-" * 50)
    print("☠️  BARBAR v8.0 (NÜKLEER SEÇENEK: SELENIUM + YT-DLP)")
    print("-" * 50)
    print("Mantık: Selenium linki bulur, yt-dlp indirir (Parçalı video sorununu çözer).")

    # Klasör oluştur
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
        print("🚨 GÖREV ZAMANI:")
        print("1. Instagram'a GİRİŞ YAP.")
        print("2. 'Şifre Kaydedilsin mi?' -> 'Şimdi Değil'.")
        print(f"3. Hedef profile git: {HEDEF_PROFIL_URL}")
        print("4. Sayfayı biraz scroll et.")
        print("5. Buraya dön ve ENTER'a bas.")
        print("="*60 + "\n")
        input("👉 Hazır mısın? Enter'a bas...")

        # --- 1. COOKIE TRANSFERİ (Çok Kritik) ---
        print("\n🍪 Oturum anahtarları yt-dlp için hazırlanıyor...")
        cookies = driver.get_cookies()
        cookie_file = os.path.join(SCRIPT_DIR, "temp_cookies.txt")
        
        # Netscape formatında cookie dosyası oluştur (yt-dlp bunu sever)
        with open(cookie_file, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            for cookie in cookies:
                # domain, flag, path, secure, expiration, name, value
                domain = cookie.get('domain', '')
                flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                path = cookie.get('path', '/')
                secure = 'TRUE' if cookie.get('secure') else 'FALSE'
                expiry = str(int(cookie.get('expiry', time.time() + 3600)))
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
        
        print("✅ Cookie dosyası oluşturuldu.")

        # --- 2. LİNK TOPLAMA VE İNDİRME ---
        processed_links = set()
        count = 0
        
        # yt-dlp Ayarları
        ydl_opts = {
            'outtmpl': os.path.join(KLASOR_ADI, '%(upload_date)s_%(id)s.%(ext)s'), # Dosya adı formatı
            'cookiefile': cookie_file,     # Hazırladığımız cookie dosyası
            'format': 'bestvideo+bestaudio/best', # En iyi kalite
            'noplaylist': True,            # Sadece tek video
            'quiet': True,                 # Konsolu kirletme
            'no_warnings': True,
            'ignoreerrors': True,          # Hata olursa durma
        }

        while count < MAX_POST_SAYISI:
            # Linkleri bul
            elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/reel/']")
            
            # Yeni linkleri filtrele
            new_links = []
            for el in elements:
                try:
                    url = el.get_attribute('href')
                    if url and url not in processed_links:
                        if '/p/' in url or '/reel/' in url:
                            new_links.append(url)
                except: pass
            
            if not new_links:
                print("🔄 Scroll yapılıyor...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                continue

            print(f"\n📊 Bulunan yeni link sayısı: {len(new_links)}")

            # --- İNDİRME DÖNGÜSÜ ---
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for url in new_links:
                    if count >= MAX_POST_SAYISI: break
                    if url in processed_links: continue
                    
                    processed_links.add(url)
                    count += 1
                    
                    print(f"⬇️  [{count}] İndiriliyor: {url}")
                    try:
                        # yt-dlp, parçalı videoları (DASH) otomatik birleştirir
                        ydl.download([url])
                        # Çok hızlı gitmemek için minik bekleme
                        time.sleep(2)
                    except Exception as e:
                        print(f"❌ Hata: {e}")

            # Limit kontrolü
            if count >= MAX_POST_SAYISI:
                print("✅ Hedef sayıya ulaşıldı.")
                break
                
            # Scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    except Exception as e:
        print(f"\n❌ GENEL HATA: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Geçici cookie dosyasını sil
        if os.path.exists(os.path.join(SCRIPT_DIR, "temp_cookies.txt")):
            try:
                os.remove(os.path.join(SCRIPT_DIR, "temp_cookies.txt"))
                print("🧹 Temizlik yapıldı.")
            except: pass
            
        print(f"\n✅ İŞLEM BİTTİ. Dosyalar: {KLASOR_ADI}")
        input("Kapatmak için Enter...")
        driver.quit()

if __name__ == "__main__":
    barbar_v8_nuclear()