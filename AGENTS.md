# AGENTS.md — SKAL Kütüphanesi Mühendislik ve Mimari Kılavuzu

Bu belge, **Çiğli Sezai Karakoç Anadolu Lisesi (SKAL) Kütüphanesi** kod tabanında çalışan tüm geliştiriciler ve yapay zeka kodlama ajanları için tekil doğruluk kaynağıdır (Single Source of Truth). Görsel tasarım jetonları ve bileşen kuralları için [`DESIGN.md`](DESIGN.md) dosyasını okuyun.

---

## 1. Proje Özeti ve Mimari Vizyon

SKAL Kütüphanesi, **Django 6.0** ve **Django Unfold** üzerine inşa edilmiş, iki katmanlı bir okul kütüphanesi yönetim ve katalog sistemidir:

1. **Halka Açık Salt-Okunur Katalog (Public Read-Only):**
   - **Vitrin (`/`):** Okul kimliğini yansıtan editoryal karşılama sayfası, canlı kütüphane istatistikleri, öne çıkan eserler, hızlı arama kapsülü ve 3 adımlı fiziksel ödünç alma rehberi.
   - **Mobil Öncelikli Arama ve Katalog (`/search/` ve `/books/`):** Öğrencilerin telefonlarından veya bilgisayarlarından giriş yapmadan kitap/yazar aradığı (`q`), durum filtrelediği (`status=available|borrowed`) ve sıraladığı (`sort=newest|name|author|due_date`) katalog ekranı.
   - **Sıfır Son Kullanıcı Girişi:** Öğrenciler için kayıt, giriş (`/accounts/login/`) veya web üzerinden ödünç/iade talebi gönderme akışı yoktur. Halka açık sayfalar tamamen `GET` tabanlı ve salt-okunurdur.
2. **Kütüphane Görevlisi Yönetim Paneli (`/admin/`):**
   - Yalnızca yetkili kütüphane görevlileri ve okul yöneticileri tarafından kullanılır (Django Unfold arayüzü).
   - Öğrenci kayıtları (`Student`), kitap envanteri (`Book`), ödünç verme ve iade alma işlemleri yalnızca `/admin/` üzerinden yürütülür.

---

## 2. Alan Modeli (Domain Model) ve İş Kuralları

Tüm iş mantığı `library/models.py` içinde kapsüllenmiştir. Görünümler (views) veya admin aksiyonları model kurallarını atlayamaz (bypass edemez).

### 2.1. `Student` (Öğrenci) Modeli ve Mezuniyet Yaşam Döngüsü
- **Alanlar:**
  - `id`: `UUIDField` (Primary Key, `uuid.uuid4`).
  - `full_name`: `CharField` (Öğrencinin adı ve soyadı).
  - `student_number`: `CharField` (`unique=True`, okul öğrenci numarası, örn. `"1042"`).
  - `graduation_year`: `PositiveIntegerField` (Mezuniyet yılı, örn. `2026`).
  - `created_at`: `DateTimeField(auto_now_add=True)`.
- **Akademik Takvim Mezuniyet Kuralı (1 Temmuz Sınırı):**
  - `Student.current_academic_cutoff_year(today=None)` metodu aktif akademik sınır yılını hesaplar:
    - Tarih **1 Temmuz veya sonrasıysa** (`month >= 7`): sınır yılı `today.year` olur (örn. `1 Temmuz 2026` tarihinde `graduation_year <= 2026` olanlar mezundur).
    - Tarih **1 Temmuz'dan önceyse** (`month < 7`): sınır yılı `today.year - 1` olur (örn. `15 Haziran 2026` tarihinde `2026` mezunları henüz aktif öğrencidir; yalnızca `<= 2025` olanlar mezundur).
  - `student.is_graduated(today=None)` özelliği bu kurala göre `bool` döner.
- **Zimmet Kilidi (`models.PROTECT`) ve Otomatik Silme (`Student.purge_graduated`):**
  - `Book.borrowed_by` alanı `Student` modeline `on_delete=models.PROTECT` (`related_name='borrowed_books'`) ile bağlıdır.
  - `Student.purge_graduated(today=None)` çağrıldığında:
    1. Mezuniyet yılı gelmiş ve **üzerinde ödünç kitap bulunmayan** (`borrowed_books__isnull=True`) öğrenciler veritabanından otomatik silinir.
    2. Mezuniyet yılı gelmiş ancak **üzerinde iade edilmemiş kitap bulunan** öğrenciler silinmez (`PROTECT` ve sorgu filtresi ile korunur).
    3. Bu öğrencinin üzerindeki son kitap kütüphane görevlisi tarafından iade alındığı anda (`Book` durumu `returned` olduğunda), öğrencinin başka zimmetli kitabı kalmadıysa mezun öğrenci kaydı otomatik olarak temizlenir.
  - Yönetim komutu: `python manage.py purge_graduated_students` (cron/zamanlanmış görev veya admin aksiyonu olarak güvenle çalıştırılabilir).

### 2.2. `Book` (Kitap) Modeli ve Otomatik Durum Senkronizasyonu
- **Alanlar:**
  - `id`: `UUIDField` (Primary Key, `uuid.uuid4`).
  - `name`: `CharField` (Kitap adı).
  - `author`: `CharField` (Yazar adı).
  - `cover`: `ImageField` (`upload_to='covers/'`, maksimum `2MB`, yalnızca `jpg, jpeg, png, webp`).
  - `status`: `CharField` — Yalnızca iki geçerli durum vardır:
    - `'returned'` (**Rafta / Müsait**)
    - `'approved'` (**Ödünç Verildi**)
  - `borrowed_by`: `ForeignKey(Student, on_delete=models.PROTECT, null=True, blank=True, related_name='borrowed_books')`.
  - `borrowed_at`: `DateField(null=True, blank=True)` (Ödünç verilme tarihi).
  - `due_date`: `DateField(null=True, blank=True)` (Son iade tarihi; varsayılan ödünç süresi `DEFAULT_LOAN_DAYS = 14` gündür).
- **Otomatik Durum ve Tarih Senkronizasyonu (`clean()` ve `save()`):**
  - Kütüphane görevlisi bir kitaba `borrowed_by` (Öğrenci) atadığında:
    - `status` otomatik olarak `'approved'` (Ödünç Verildi) yapılır.
    - `borrowed_at` boşsa bugünün tarihi (`timezone.localdate()`) atanır.
    - `due_date` boşsa `borrowed_at + timedelta(days=14)` atanır.
  - Kütüphane görevlisi `borrowed_by` alanını temizlediğinde veya `status='returned'` seçtiğinde (`mark_returned()`):
    - `status = 'returned'`, `borrowed_by = None`, `borrowed_at = None`, `due_date = None` olarak sıfırlanır.
    - İade eden öğrenci mezun durumdaysa ve üzerinde başka kitap kalmadıysa öğrenci kaydı otomatik silinir.
  - `status='approved'` seçilip `borrowed_by` boş bırakılırsa `ValidationError` fırlatılır.
- **Veritabanı Bütünlük Kısıtı (`CheckConstraint`):**
  - `book_status_borrower_consistency`: Veritabanı seviyesinde `(status == 'returned' AND borrowed_by IS NULL AND borrowed_at IS NULL AND due_date IS NULL) OR (status == 'approved' AND borrowed_by IS NOT NULL AND due_date IS NOT NULL)` kuralını zorunlu kılar.

### 2.3. KVKK ve Öğrenci Gizliliği Kuralı (Kritik)
- Halka açık hiçbir sayfada (`/`, `/search/`, `/books/`), HTML şablonunda, DOM veri özniteliğinde (`data-*`) veya açık uç noktada **ödünç alan öğrencinin adı (`full_name`) veya öğrenci numarası (`student_number`) asla yer almaz.**
- Ziyaretçiler yalnızca kitabın durumunu (`Müsait` veya `Ödünçte`) ve ödünçteyse `due_date` (**İade Tarihi: GG.AA.YYYY**) bilgisini görür.

---

## 3. Mühendislik İlkeleri ("The Django Way")

- **Fat Models, Skinny Views:** İş kuralları, tarih hesaplamaları ve durum geçişleri `library/models.py` içinde tanımlanır. Görünümler (`library/views.py`) yalnızca HTTP parametrelerini (`q`, `status`, `sort`) doğrular, sorguyu çalıştırır ve şablonu döndürür.
- **Veri Bütünlüğü ve Eşzamanlılık:** Durum değiştiren tüm admin aksiyonları ve toplu işlemler `transaction.atomic()` ve `select_for_update()` kilidi altında çalışır.
- **N+1 Sorgu Koruması:** Kitap listeleme ve yönetim sorgularında `Book.objects.select_related('borrowed_by')` kullanımı zorunludur. Halka açık sayfalar sabit sorgu bütçesiyle çalışır.
- **Kapak Görseli Güvenliği:** `cover` alanı `FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])` ve `validate_cover_image` (maksimum `2 * 1024 * 1024` bayt = 2MB) ile korunur.
- **Üretim Güvenliği (Fail-Closed):** `config/settings.py` içinde `DEBUG=False` iken `DJANGO_SECRET_KEY` ortam değişkeni tanımlı değilse uygulama `ImproperlyConfigured` hatası vererek başlatmayı reddeder.

---

## 4. Tasarım Sistemi ve Frontend Standartları (`DESIGN.md` Referansı)

Halka açık tüm şablonlar (`library/templates/library/`) [`DESIGN.md`](DESIGN.md) içindeki **SKAL Kütüphanesi (Dyotanya Editorial Sketchbook)** tasarım sistemini uygular:

1. **Yalnızca Açık Tema (Strictly Light Mode):**
   - `:root` ve `html` üzerinde `color-scheme: light !important` zorunludur. Koyu mod (dark mode) veya koyu arka planlı bölüm geçişleri kullanılmaz.
2. **Okul Logosu ve Kağıt Renk Paleti:**
   - Zemin (Warm Paper): `#f5f5f3` (`--color-warm-paper`)
   - Ana Metin ve 1.5px Çizgiler (Ink Black): `#121124` (`--color-ink-black`)
   - Kurumsal Lacivert ve Sert Gölge (SKAL Navy): `#282471` (`--color-charcoal` / `--color-skal-navy`)
   - Kart Yüzeyi (Pure White): `#ffffff` (`--color-pure-white`)
   - Dekoratif Kart/Girdi Çerçevesi (Dusty Indigo): `#5c58a6` (`--color-dusty-sky`)
   - Odak/Hover Çerçevesi (Cobalt Wash): `#3b368c` (`--color-cobalt-wash`)
   - Başak Turuncusu Vurgu ve Bağlantı (SKAL Orange): `#ec782b` (`--color-coral-link` / `--color-skal-orange`)
3. **Tipografi ve Editoryal Ses:**
   - Başlıklar ve Kitap Adları: `'Playfair Display'` (`--font-simeiz`), Türkçe karakterleri (`ğ, ü, ş, i, ö, ç, İ`) eksiksiz destekler. Ana başlıklarda düz (roman) ve *italik* kelimeler bir arada kullanılarak editoryal ritim oluşturulur.
   - Arayüz, Gövde ve Rozetler: `'Manrope'` (`--font-manrope`), `-0.02em` ile `-0.036em` harf aralığı.
4. **Yüzey, Gölge ve El Çizimi Motifler:**
   - Bulanık (blur) gölge kullanılmaz. Kartlarda `5px -5px 0px 0px #282471`, kapsül buton ve arama çubuğunda `4px -4px 0px 0px #282471` sert ofset gölge kullanılır.
   - Birincil butonlar, arama çubuğu ve filtre çipleri `3000px` (`--radius-pills`) kapsül köşelidir; kitap kartları `24px–30px` köşe yuvarlaklığına sahiptir.
   - Bölümler arasında `1.5px` kalınlığında `#121124` el çizimi görünümünde satır içi `<svg>` çizgiler kullanılır.
5. **Mobil Öncelikli Ergonomi:**
   - Tüm etkileşimli öğeler (arama çubuğu, temizle butonu, filtre çipleri, sıralama seçicisi) minimum `44px × 44px` (`48px` önerilen) dokunma alanına sahiptir.
   - `360px`, `768px`, `1024px` ve `1440px` ekran genişliklerinde yatay taşma (`overflow-x`) sıfır olmalıdır.

---

## 5. Geliştirme, Test ve Doğrulama Komutları

Her kod değişikliği **Test-Driven Development (Red-Green-Refactor)** döngüsüyle geliştirilir ve görev tamamlanmadan önce aşağıdaki doğrulama komutlarının tamamı sıfır hata ile geçmelidir:

```bash
# 1. Sistem ve yapılandırma kontrolü
python manage.py check

# 2. Eksik veya bekleyen veritabanı taşıması (migration) olmadığının doğrulanması
python manage.py makemigrations --check --dry-run

# 3. Tüm birim, entegrasyon, güvenlik ve performans testlerinin çalıştırılması
python manage.py test --verbosity=2

# 4. Mezun öğrenci temizleme komutunun doğrulanması
python manage.py purge_graduated_students --dry-run
```

### Tamamlanma Kriterleri (Definition of Done)
- [ ] Yeni veya değişen her davranış için önce başarısız olan bir test yazıldı ve ardından minimum üretim koduyla geçirildi.
- [ ] `python manage.py test` komutu sıfır hata ve sıfır başarısızlık ile tamamlandı.
- [ ] `python manage.py makemigrations --check --dry-run` çıktısı model ve migration dosyalarının tam senkronize olduğunu doğruladı.
- [ ] Halka açık şablonlarda öğrenci adı veya öğrenci numarası sızıntısı olmadığı testlerle kanıtlandı.
- [ ] Tüm arayüz bileşenleri [`DESIGN.md`](DESIGN.md) içerisindeki açık tema, renk jetonları ve mobil ergonomi kurallarıyla birebir uyumlu.
