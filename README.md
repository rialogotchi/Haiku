# Haiku + Future teması paketi

## İçerik
- `.github/workflows/build-haiku-image.yml` : elle tetiklenen (`workflow_dispatch`) imaj build'i
- `theme/` : Future KDE temasının Haiku'ya uyarlanmış hali

## Kurulum (Haiku fork'unda)
1. Bu klasördeki `.github/` ve `theme/` dizinlerini Haiku deposunun köküne kopyala, push et.
2. GitHub → **Actions → Build Haiku image → Run workflow**.
3. Seçenekler: mimari (`x86_64` / `x86_gcc2h`), hedef (`nightly-raw` = **.img**, `*-anyboot` = USB'ye yazılabilir .iso, `nightly-vmware`), imaj boyutu, tema açık/kapalı, `Future`/`FutureDark`, xz sıkıştırma, Release oluşturma.
4. Çıktı: run sayfasındaki **Artifacts** bölümünde `haiku-<mimari>-<hedef>.img`.

İlk build cross-compiler'ı derlediği için uzun sürer (genelde 1–3 saat). Runner disk/süre sınırı: 6 saat.

## Tema: ne taşındı, ne taşınamadı
KDE temasının Aurorae (KWin pencere süsü), Plasma masaüstü teması, SDDM ve look-and-feel kısımları Haiku'da karşılığı olmayan bileşenler; bunlar taşınamaz. Haiku'da çalışan karşılığı **sistem renk paleti**:

- `kde2haiku.py`, KDE `.colors` dosyasını Haiku'nun `~/config/settings/system/app_server/appearance` dosyasına çevirir (39 `ui_color` değeri; eşleme tablosu betiğin içinde, istediğin rengi değiştirebilirsin).
- Hazır çıktılar: `theme/Future/appearance`, `theme/FutureDark/appearance`.
- Duvar kağıtları: `theme/wallpapers/`.
- `theme/kvantum-opsiyonel/`: Kvantum Haiku'da kuruluysa Qt uygulamaları için; test edilmedi.

Imaja gömmek için workflow'da `apply_theme` açık kalsın; elle kurmak için Haiku içinde:
```
bash theme/install-theme.sh Future      # veya FutureDark
```
sonra oturumu kapat/aç (app_server renkleri açılışta okur).

Yeni renk üretmek: `python3 theme/kde2haiku.py baska.colors -o appearance`

## Test durumu (dürüst not)
- Çevrilen `appearance` dosyasının ikili biçimi, Haiku kaynağındaki `Message.cpp` / `DesktopSettings.cpp` okunarak yazıldı ve bir doğrulayıcıyla (başlık, hash tablosu, alan sınırları) kontrol edildi. **Gerçek Haiku'da veya Actions'ta çalıştırılmadı.**
- Workflow YAML olarak ayrıştırıldı ve UserBuildConfig üreten adım yerelde denendi; tam build denenmedi.
- Pencere başlık çubuğu renkleri KDE'nin `[WM]` değerlerinden geliyor; Future açık temada neredeyse beyaz, aktif/pasif pencere farkı az görünebilir. Beğenmezsen `WINDOW_TAB` satırını `sel_bg` yap.

## Lisans / uyarı
- Tema renkleri ve duvar kağıtları Future-kde'den (GPL v3, yeyushengfan258) türetildi; `theme/LICENSE-Future-kde-GPLv3`.
- Haiku deposundaki `AGENTS.md`, Haiku'ya yapılacak katkılarda yapay zekâ üretimi kodu kabul etmediğini söylüyor. Bu paketi sadece kendi fork'unda kullanırsan sorun yok; upstream'e PR göndermeyi düşünüyorsan buradaki dosyaları gönderme.
