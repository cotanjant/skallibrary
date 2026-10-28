/*!
 * SKAL Kütüphanesi - Yönetim Paneli İnteraktif Kullanım Rehberi (Onboarding Tour)
 * Sadelik, yüksek erişilebilirlik ve antislop kurallarına uygun olarak hazırlanmıştır.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'skal_admin_tour_completed';

  /**
   * Sayfadaki uygun öğeleri belirleyen ve hedef bulunamadığında
   * sessizce sonraki adıma geçen adım tanımları.
   */
  var STEP_DEFINITIONS = [
    {
      id: 'welcome',
      selectors: ['#header-inner', '#header', 'header', '#main'],
      title: 'SKAL Kütüphanesi Yönetim Paneline Hoş Geldiniz',
      description: 'Bu rehber; kayıtlı öğrencilere son iade tarihiyle kitap ödünç verme, geciken kitapları takip etme ve mezuniyet yılına göre öğrenci yönetimi iş akışlarını tanıtır.',
      side: 'bottom',
      allowFallbackToCenter: true,
    },
    {
      id: 'navigation',
      selectors: ['#nav-sidebar', 'nav#nav-sidebar', '.navigation_wrapper', 'aside'],
      title: 'Sol Menü: Kitaplar ve Öğrenciler',
      description: 'Sol menüden Kitap Kataloğu ve Öğrenci Kayıtları ekranlarına doğrudan geçiş yapabilirsiniz. Öğrencileri okul numarası ve mezuniyet yılı bilgileriyle buradan yönetebilirsiniz.',
      side: 'right',
      allowFallbackToCenter: false,
    },
    {
      id: 'dashboard',
      selectors: ['#content-main', '#content', '.app-library', '.module:not(.filtered)'],
      title: 'Gösterge Paneli: Ödünçteki ve Geciken Kitaplar',
      description: 'Şu anda öğrencilerde bulunan tüm kitapları, son iade tarihlerini ve süresi geçen gecikmiş iadeleri bu panelden anlık olarak takip edebilir, tek tıkla iade alabilirsiniz.',
      side: 'bottom',
      allowFallbackToCenter: true,
    },
    {
      id: 'catalog_filters',
      selectors: ['#changelist-filter', '#changelist .filtered', '#changelist', 'a[href*="/library/book/"]'],
      title: 'Kitap Atama ve Son İade Tarihi',
      description: 'Bir kitabı düzenleyerek kayıtlı öğrenciye doğrudan ödünç verebilir, son iade tarihini (varsayılan 14 gün) belirleyebilir ve durum filtresiyle müsait ya da ödünçteki eserleri süzebilirsiniz.',
      side: 'left',
      allowFallbackToCenter: false,
    },
    {
      id: 'bulk_actions',
      selectors: ['#changelist-actions', '.actions', 'form#changelist-form .actions', 'select[name="action"]'],
      title: 'Toplu İade ve Mezun Öğrenci Temizliği',
      description: 'Kitap listesinde seçili kitapların iadesini topluca alabilir; öğrenci listesinde ise mezuniyet yılı geçmiş öğrencileri güvenli toplu işlemle temizleyebilirsiniz.',
      side: 'top',
      allowFallbackToCenter: false,
    },
    {
      id: 'completion',
      selectors: ['#skal-start-tour-btn', '#header-inner', '#header'],
      title: 'Rehber Tamamlandı',
      description: 'Yönetim paneli tanıtımını tamamladınız. Rehbere dilediğiniz zaman üst çubuktaki Rehberi Başlat butonundan yeniden ulaşabilirsiniz.',
      side: 'bottom',
      allowFallbackToCenter: true,
    },
  ];

  /**
   * Driver motor referansını güvenle çözer.
   */
  function getDriverFactory() {
    if (typeof window.driver === 'function') {
      return window.driver;
    }
    if (window.driver && typeof window.driver.driver === 'function') {
      return window.driver.driver;
    }
    if (window.driver && window.driver.js && typeof window.driver.js.driver === 'function') {
      return window.driver.js.driver;
    }
    if (typeof window.Driver === 'function') {
      return window.Driver;
    }
    return null;
  }

  /**
   * CSS seçici dizisinden DOM'da var olan ilk görünür öğeyi bulur.
   */
  function findFirstMatchingElement(selectors) {
    if (!selectors || !selectors.length) return null;
    for (var i = 0; i < selectors.length; i++) {
      try {
        var el = document.querySelector(selectors[i]);
        if (el) {
          var rect = el.getBoundingClientRect();
          if (rect.width > 0 || rect.height > 0 || el.offsetParent !== null) {
            return el;
          }
        }
      } catch (err) {
        // Geçersiz seçici durumunda sessizce devam et
      }
    }
    return null;
  }

  /**
   * Mevcut sayfada bulunan öğelere göre adımları dinamik ve hatasız filtreler.
   */
  function buildActiveSteps() {
    var validSteps = [];

    for (var i = 0; i < STEP_DEFINITIONS.length; i++) {
      var def = STEP_DEFINITIONS[i];
      var el = findFirstMatchingElement(def.selectors);

      if (el) {
        validSteps.push({
          element: el,
          popover: {
            title: def.title,
            description: def.description,
            side: def.side,
          },
        });
      } else if (def.allowFallbackToCenter) {
        validSteps.push({
          element: null,
          popover: {
            title: def.title,
            description: def.description,
            side: 'center',
          },
        });
      }
      // allowFallbackToCenter = false ve öğe sayfada yoksa adım atlanır (fail-safe)
    }

    return validSteps;
  }

  /**
   * Admin üst çubuğuna veya sayfaya "Rehberi Başlat" butonunu enjekte eder.
   */
  function injectStartTourButton(onStartCallback) {
    if (document.getElementById('skal-start-tour-btn')) {
      return;
    }

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'skal-start-tour-btn';
    btn.title = 'Kullanım Rehberini Başlat';
    btn.setAttribute('aria-label', 'Kullanım Rehberini Başlat');

    btn.innerHTML = [
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">',
      '  <circle cx="12" cy="12" r="10"></circle>',
      '  <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>',
      '</svg>',
      '<span>Rehberi Başlat</span>',
    ].join('');

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      if (typeof onStartCallback === 'function') {
        onStartCallback();
      }
    });

    // Unfold veya Django Admin yapısına göre en uygun noktaya ekle
    var container = (
      document.querySelector('#header-inner .ml-auto') ||
      document.querySelector('#header-inner') ||
      document.querySelector('header .flex.items-center.ml-auto') ||
      document.querySelector('header') ||
      document.querySelector('#user-tools')
    );

    if (container) {
      container.insertBefore(btn, container.firstChild);
    } else {
      // Header bulunamazsa sağ alta yüzen (floating) buton olarak yerleştir
      btn.classList.add('skal-tour-floating');
      document.body.appendChild(btn);
    }
  }

  /**
   * Ana Tur Yöneticisi
   */
  function initAdminTour() {
    var driverFactory = getDriverFactory();
    if (!driverFactory) {
      // Driver.js henüz yüklenmediyse kısa süre sonra yeniden dene
      setTimeout(initAdminTour, 150);
      return;
    }

    var tourInstance = null;

    function startTour() {
      var steps = buildActiveSteps();
      if (!steps || steps.length === 0) return;

      if (tourInstance) {
        tourInstance.destroy();
      }

      tourInstance = driverFactory({
        steps: steps,
        animate: true,
        overlayColor: 'rgba(15, 23, 42, 0.65)',
        stagePadding: 8,
        stageRadius: 6,
        allowClose: true,
        popoverClass: 'skal-tour-popover',
        nextBtnText: 'Sonraki Adım',
        prevBtnText: 'Önceki Adım',
        doneBtnText: 'Rehberi Tamamla',
        closeBtnText: 'Atla',
        showProgress: true,
        progressText: '{{current}} / {{total}}',
        onDestroyed: function () {
          try {
            localStorage.setItem(STORAGE_KEY, 'true');
          } catch (e) {}
        },
      });

      tourInstance.drive(0);
    }

    // "Rehberi Başlat" butonunu enjekte et
    injectStartTourButton(function () {
      startTour();
    });

    // İlk girişte otomatik başlatma kontrolü
    try {
      var isCompleted = localStorage.getItem(STORAGE_KEY);
      if (!isCompleted) {
        setTimeout(function () {
          startTour();
        }, 600);
      }
    } catch (e) {
      // localStorage erişim kısıtlıysa sessizce geç
    }

    // Genel erişim için pencereye bağla
    window.skalAdminTour = {
      start: startTour,
      reset: function () {
        try {
          localStorage.removeItem(STORAGE_KEY);
        } catch (e) {}
        startTour();
      },
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAdminTour);
  } else {
    initAdminTour();
  }
})();
