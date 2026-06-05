import streamlit as st
import requests

# ============================================================
# AYARLAR
# ============================================================
STRAPI_URL = "https://gezi-rehberi-1-nf3e.onrender.com"

# ============================================================
# SAYFA AYARLARI
# ============================================================
st.set_page_config(
    page_title="Gezi Rehberi",
    page_icon="🗺️",
    layout="wide"
)

# ============================================================
# STİL
# ============================================================
st.markdown("""
    <style>
    .mekan-kart {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #e0e0e0;
    }
    .mekan-adi {
        font-size: 20px;
        font-weight: bold;
        color: #1a1a2e;
    }
    .puan {
        font-size: 16px;
        color: #f4a261;
        font-weight: bold;
    }
    .aciklama {
        font-size: 14px;
        color: #444;
        margin-top: 8px;
    }
    .baslik {
        text-align: center;
        color: #1a1a2e;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# FONKSİYONLAR
# ============================================================
@st.cache_data(ttl=60)
def sehirleri_getir():
    """Strapi'den şehirleri çeker."""
    try:
        resp = requests.get(
            f"{STRAPI_URL}/api/cities",
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get("data", [])
    except Exception as e:
        st.error(f"Şehirler yüklenemedi: {e}")
    return []
@st.cache_data(ttl=60)
def mekanlari_getir(sehir_doc_id):
    """Strapi'den seçili şehrin mekanlarını çeker."""
    try:
        resp = requests.get(
            f"{STRAPI_URL}/api/places",
            params={
                "populate": "*",
                "filters[city][documentId][$eq]": sehir_doc_id,
            },
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get("data", [])
    except Exception as e:
        st.error(f"Mekanlar yüklenemedi: {e}")
    return []

# ============================================================
# ARAYÜZ
# ============================================================
st.markdown("<h1 class='baslik'>🗺️ Gezi Rehberi</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666;'>Türkiye'nin güzel şehirlerini keşfedin</p>", unsafe_allow_html=True)
st.divider()

# Şehirleri yükle
sehirler = sehirleri_getir()

if not sehirler:
    st.warning("Şehirler yüklenemedi. Lütfen sayfayı yenileyin.")
    st.stop()

# Şehir seçimi
sehir_adlari = [s["Name"] for s in sehirler]
secilen_ad = st.selectbox("🏙️ Bir şehir seçin:", sehir_adlari)

# Seçilen şehri bul
secilen_sehir = next((s for s in sehirler if s["Name"] == secilen_ad), None)

if secilen_sehir:
    # Şehir bilgisi
    st.markdown(f"### 📍 {secilen_sehir['Name']}, {secilen_sehir['Country']}")
    st.info(secilen_sehir.get("Description", ""))
    st.divider()

    # Mekanları yükle
    with st.spinner("Mekanlar yükleniyor..."):
        mekanlar = mekanlari_getir(secilen_sehir["documentId"])

    if not mekanlar:
        st.warning("Bu şehre ait mekan bulunamadı.")
    else:
        st.markdown(f"### 🏛️ {secilen_ad} Mekanları ({len(mekanlar)} mekan)")
        
        # 3'lü grid
        cols = st.columns(3)
        for i, mekan in enumerate(mekanlar):
            with cols[i % 3]:
                # Görsel
                image = mekan.get("Image")
                if image and image.get("url"):
                    gorsel_url = STRAPI_URL + image["url"]
                    st.image(gorsel_url, use_container_width=True)
                
                # Bilgiler
                st.markdown(f"**{mekan['Name']}**")
                puan = mekan.get("Rating", 0)
                st.markdown(f"⭐ {puan}/10")
                st.markdown(mekan.get("Description", ""))
                st.divider()