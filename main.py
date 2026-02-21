import os
from instagrapi import Client
from openai import OpenAI
import time

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

def login_instagram():
    print("📱 Instagram'a giriş yapılıyor...")
    
    try:
        # User agent değiştir ve cookie kullan
        cl = Client(
            use_alternative_instagram_agent=True,
            use_cookie=True
        )
        
        time.sleep(1)
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        print(f"✅ Giriş başarılı! {INSTAGRAM_USERNAME}")
        return cl
    
    except Exception as e:
        print(f"❌ Giriş hatası: {e}")
        print("\n🔄 İkinci deneme yapılıyor...")
        
        try:
            time.sleep(3)
            cl = Client()
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            print(f"✅ Giriş başarılı! {INSTAGRAM_USERNAME}")
            return cl
        except Exception as e2:
            print(f"❌ İkinci deneme de başarısız: {e2}")
            return None

def get_my_posts(cl):
    print("\n📸 Senin post'ların çekiliyor...")
    
    try:
        user_id = cl.user_id
        medias = cl.user_medias(user_id, amount=10)
        
        posts = []
        for media in medias:
            posts.append({
                "caption": media.caption if media.caption else "No caption",
                "likes": media.like_count,
                "comments": media.comment_count,
                "type": "Reel" if media.media_type == 8 else "Post"
            })
        
        print(f"✅ {len(posts)} post çekildi!")
        for i, p in enumerate(posts, 1):
            cap = p["caption"][:40] if p["caption"] else "Yazı yok"
            print(f"  {i}. {cap}... ({p['likes']} beğeni)")
        
        return posts
    
    except Exception as e:
        print(f"❌ Post çekme hatası: {e}")
        return None

def analyze_my_style(posts):
    print("\n🤖 OpenAI ile analiz yapılıyor...")
    
    if not posts:
        return None
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        captions_text = "\n".join([p["caption"] for p in posts])
        
        prompt = f"""Instagram post'larini analiz et:

{captions_text}

SORULAR:
1. Stil nedir?
2. Ana tema nedir?
3. Hashtag'ler?
4. Emoji kullanimi?
5. Call to Action?
6. Ortalama uzunluk?
7. Iceriginin ozu?"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = response.choices[0].message.content
        print(f"\n✅ Analiz tamamlandi!\n{analysis}")
        return analysis
    
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None

def create_similar_captions(analysis):
    print("\n✍️ Benzer caption'lar olusturuluyor...")
    
    if not analysis:
        return None
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""Stil profiline uygun 5 farkli caption olustur:

{analysis}

KURALLAR:
- 100-200 karakter
- 3-5 emoji
- 5-7 hashtag
- Call to Action
- Benzer stil

SADECE CAPTION'LAR!"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        captions = response.choices[0].message.content
        print(f"\n✅ Caption'lar olusturuldu!")
        print(captions)
        return captions
    
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None

def main():
    print("=" * 70)
    print("🚀 SENIN INSTAGRAM ANALIZI - GITHUB ACTIONS")
    print("=" * 70)
    
    # Giriş
    cl = login_instagram()
    if not cl:
        print("\n❌ Giriş basarısız!")
        return
    
    # Post'ları çek
    posts = get_my_posts(cl)
    if not posts:
        print("\n❌ Post çekme basarısız!")
        return
    
    # Analiz yap
    analysis = analyze_my_style(posts)
    if not analysis:
        print("\n❌ Analiz basarısız!")
        return
    
    # Caption'lar oluştur
    captions = create_similar_captions(analysis)
    if not captions:
        print("\n❌ Caption olusturma basarısız!")
        return
    
    print("\n" + "=" * 70)
    print("✅ TAMAMLANDI!")
    print("=" * 70)

if __name__ == "__main__":
    main()
