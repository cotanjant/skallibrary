from datetime import date, timedelta
import importlib
import io
import os
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from django.conf import settings
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from library.admin import (
    BookAdmin,
    StudentAdmin,
    mark_books_returned,
    purge_graduated_action,
)
from library.dashboard import (
    dashboard_callback,
    overdue_books_badge,
    pending_books_badge,
)
from library.models import Book, Student

User = get_user_model()


class MockModelAdmin:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def message_user(self, request, message: str) -> None:
        self.messages.append(message)


class PublicCatalogAndSearchTests(TestCase):
    """Halka açık vitrin, arama ve katalog sayfalarının fonksiyonel, gizlilik ve sorgu bütçesi testleri."""

    def setUp(self) -> None:
        self.student = Student.objects.create(
            full_name="Ahmet Yılmaz",
            student_number="1453",
            graduation_year=2028,
        )
        self.today = timezone.localdate()
        self.due = self.today + timedelta(days=10)

        self.available_book = Book.objects.create(
            name="Çalıkuşu",
            author="Reşat Nuri Güntekin",
            status="returned",
        )
        self.borrowed_book = Book.objects.create(
            name="Tutunamayanlar",
            author="Oğuz Atay",
            status="approved",
            borrowed_by=self.student,
            borrowed_at=self.today,
            due_date=self.due,
        )

    def test_public_auth_and_self_borrow_endpoints_removed(self) -> None:
        """Öğrenci giriş/kayıt ve self-servis ödünç/iade uç noktalarının tamamen kaldırıldığını (404) doğrular."""
        removed_paths = [
            "/accounts/login/",
            "/accounts/signup/",
            "/accounts/logout/",
            f"/borrow/{self.available_book.id}/",
            f"/return/{self.borrowed_book.id}/",
        ]
        for path in removed_paths:
            with self.subTest(path=path):
                get_resp = self.client.get(path)
                self.assertEqual(get_resp.status_code, 404)
                post_resp = self.client.post(path)
                self.assertEqual(post_resp.status_code, 404)

    def test_home_vitrin_renders_and_query_budget(self) -> None:
        """Ana vitrin sayfasının (/) 200 döndüğünü, KPI metriklerini sunduğunu ve 2 sorguda çalıştığını doğrular."""
        with self.assertNumQueries(2):
            response = self.client.get(reverse("home"))
            self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["total_books"], 2)
        self.assertEqual(response.context["available_books"], 1)
        self.assertEqual(response.context["borrowed_books"], 1)
        self.assertEqual(len(response.context["featured_books"]), 2)
        self.assertContains(response, "Çalıkuşu")
        self.assertContains(response, "Tutunamayanlar")

    def test_search_and_books_routes_render_catalog(self) -> None:
        """Hem /search/ hem de /books/ rotalarının tek sorguda (O(1)) 200 yanıtı verdiğini doğrular."""
        for route_name in ("book_search", "book_list"):
            with self.subTest(route_name=route_name):
                with self.assertNumQueries(1):
                    response = self.client.get(reverse(route_name))
                    self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context["books"]), 2)

    def test_search_filtering_and_sorting(self) -> None:
        """Arama (?q=), durum filtresi (?status=) ve sıralama (?sort=) parametrelerinin doğruluğunu test eder."""
        extra_student = Student.objects.create(
            full_name="Zeynep Kaya",
            student_number="1923",
            graduation_year=2027,
        )
        early_due_book = Book.objects.create(
            name="Anayurt Oteli",
            author="Yusuf Atılgan",
            status="approved",
            borrowed_by=extra_student,
            borrowed_at=self.today - timedelta(days=5),
            due_date=self.today + timedelta(days=2),
        )

        # 1. Arama sorgusu (?q=)
        resp_q = self.client.get(reverse("book_search"), {"q": "Oğuz"})
        self.assertEqual([b.name for b in resp_q.context["books"]], ["Tutunamayanlar"])

        # 2. Müsait kitap filtresi (?status=available)
        resp_avail = self.client.get(reverse("book_search"), {"status": "available"})
        self.assertEqual([b.name for b in resp_avail.context["books"]], ["Çalıkuşu"])

        # 3. Ödünçte filtresi (?status=borrowed)
        resp_borrowed = self.client.get(reverse("book_search"), {"status": "borrowed"})
        self.assertEqual(
            {b.name for b in resp_borrowed.context["books"]},
            {"Tutunamayanlar", "Anayurt Oteli"},
        )

        # 4. Sıralama: Kitap Adı (name)
        resp_sort_name = self.client.get(reverse("book_search"), {"sort": "name"})
        self.assertEqual(
            [b.name for b in resp_sort_name.context["books"]],
            sorted([b.name for b in resp_sort_name.context["books"]]),
        )

        # 5. Sıralama: Yazar (author)
        resp_sort_author = self.client.get(reverse("book_search"), {"sort": "author"})
        self.assertEqual(
            [b.author for b in resp_sort_author.context["books"]],
            ["Oğuz Atay", "Reşat Nuri Güntekin", "Yusuf Atılgan"],
        )

        # 6. Sıralama: Önce Müsait Olanlar (availability)
        resp_sort_avail = self.client.get(reverse("book_search"), {"sort": "availability"})
        self.assertEqual(resp_sort_avail.context["books"][0].name, "Çalıkuşu")
        self.assertTrue(resp_sort_avail.context["books"][0].is_available)

        # 7. Sıralama: İade Tarihi Yaklaşan (due_date)
        resp_sort_due = self.client.get(
            reverse("book_search"),
            {"status": "borrowed", "sort": "due_date"},
        )
        self.assertEqual(
            [b.id for b in resp_sort_due.context["books"]],
            [early_due_book.id, self.borrowed_book.id],
        )

    def test_due_date_visible_but_student_identity_never_leaked(self) -> None:
        """Halka açık sayfalarda son iade tarihinin göründüğünü ancak öğrenci kimliğinin asla sızmadığını doğrular."""
        formatted_due = self.due.strftime("%d.%m.%Y")
        for url in (reverse("home"), reverse("book_search"), reverse("book_list")):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Ödünçte")
                self.assertContains(response, formatted_due)
                self.assertNotContains(response, "Ahmet Yılmaz")
                self.assertNotContains(response, "1453")

    def test_cover_placeholder_and_cover_image_display(self) -> None:
        """Kapak resmi olmadığında placeholder, olduğunda ise kapak görseli URL'sinin gösterildiğini doğrular."""
        response = self.client.get(reverse("book_search"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "book-cover-placeholder")

        image = Image.new("RGB", (100, 100), color="navy")
        byte_io = io.BytesIO()
        image.save(byte_io, format="JPEG")
        uploaded_image = SimpleUploadedFile(
            "test_cover.jpg",
            byte_io.getvalue(),
            content_type="image/jpeg",
        )

        book_with_cover = Book.objects.create(
            name="Kapaklı Kitap",
            author="Yazar",
            cover=uploaded_image,
        )
        try:
            response = self.client.get(reverse("book_search"))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, book_with_cover.cover.url)
        finally:
            if book_with_cover.cover:
                book_with_cover.cover.delete(save=False)


class StudentGraduationAndLoanLockTests(TestCase):
    """Öğrenci mezuniyet yılı hesaplaması, otomatik temizlik ve zimmet kilidi (PROTECT) testleri."""

    def test_academic_cutoff_year_calculation(self) -> None:
        """1 Temmuz öncesi ve sonrası için akademik mezuniyet sınır yılının doğru hesaplandığını test eder."""
        self.assertEqual(Student.current_graduation_cutoff_year(date(2026, 6, 15)), 2025)
        self.assertEqual(Student.current_graduation_cutoff_year(date(2026, 6, 30)), 2025)
        self.assertEqual(Student.current_graduation_cutoff_year(date(2026, 7, 1)), 2026)
        self.assertEqual(Student.current_graduation_cutoff_year(date(2026, 10, 25)), 2026)

    def test_purge_graduated_deletes_only_students_without_loans(self) -> None:
        """Zimmetsiz mezun öğrencilerin silindiğini, zimmetli mezunların ve aktif öğrencilerin korunduğunu doğrular."""
        graduated_free = Student.objects.create(
            full_name="Mezun Zimmetsiz",
            student_number="202501",
            graduation_year=2025,
        )
        graduated_with_loan = Student.objects.create(
            full_name="Mezun Zimmetli",
            student_number="202502",
            graduation_year=2025,
        )
        active_student = Student.objects.create(
            full_name="Aktif Öğrenci",
            student_number="202801",
            graduation_year=2028,
        )

        Book.objects.create(
            name="Zimmetli Kitap",
            author="Yazar",
            status="approved",
            borrowed_by=graduated_with_loan,
            borrowed_at=date(2026, 10, 1),
            due_date=date(2026, 10, 15),
        )

        deleted_count, blocked_count = Student.purge_graduated(today=date(2026, 10, 25))
        self.assertEqual(deleted_count, 1)
        self.assertEqual(blocked_count, 1)

        self.assertFalse(Student.objects.filter(id=graduated_free.id).exists())
        self.assertTrue(Student.objects.filter(id=graduated_with_loan.id).exists())
        self.assertTrue(Student.objects.filter(id=active_student.id).exists())

    def test_protect_constraint_prevents_deleting_student_with_active_book(self) -> None:
        """Üzerinde ödünç kitap bulunan öğrencinin doğrudan silinmesinin ProtectedError ile engellendiğini doğrular."""
        student = Student.objects.create(
            full_name="Korunan Öğrenci",
            student_number="9001",
            graduation_year=2026,
        )
        Book.objects.create(
            name="Korunan Kitap",
            author="Yazar",
            status="approved",
            borrowed_by=student,
        )

        with self.assertRaises(ProtectedError):
            student.delete()

    def test_returning_book_via_admin_action_purges_graduated_student(self) -> None:
        """Mezun öğrencinin zimmetindeki kitap iade alındığında mezun öğrencinin otomatik temizlendiğini doğrular."""
        graduated_student = Student.objects.create(
            full_name="Mezun İade Bekleyen",
            student_number="202499",
            graduation_year=2024,
        )
        book = Book.objects.create(
            name="İade Edilecek Kitap",
            author="Yazar",
            status="approved",
            borrowed_by=graduated_student,
        )

        mock_admin = MockModelAdmin()
        req = RequestFactory().post("/admin/library/book/")
        mark_books_returned(mock_admin, req, Book.objects.filter(id=book.id))

        book.refresh_from_db()
        self.assertEqual(book.status, "returned")
        self.assertIsNone(book.borrowed_by)
        self.assertIsNone(book.borrowed_at)
        self.assertIsNone(book.due_date)
        self.assertFalse(Student.objects.filter(id=graduated_student.id).exists())
        self.assertTrue(any("otomatik temizlendi" in m for m in mock_admin.messages))

    def test_purge_graduated_students_management_command(self) -> None:
        """purge_graduated_students yönetim komutunun mezun öğrencileri temizleyip çıktı ürettiğini doğrular."""
        graduated_student = Student.objects.create(
            full_name="Komutla Silinecek Mezun",
            student_number="202301",
            graduation_year=2023,
        )
        out = io.StringIO()
        call_command("purge_graduated_students", stdout=out)

        self.assertFalse(Student.objects.filter(id=graduated_student.id).exists())
        self.assertIn("1 mezun öğrenci kaydı silindi", out.getvalue())


class BookModelIntegrityAndSecurityTests(TestCase):
    """Kitap modeli iş kuralları, 14 gün otomatik iade süresi, CheckConstraint ve üretim güvenliği testleri."""

    def setUp(self) -> None:
        self.student = Student.objects.create(
            full_name="Elif Demir",
            student_number="1071",
            graduation_year=2029,
        )
        self.book = Book.objects.create(name="Kuyucaklı Yusuf", author="Sabahattin Ali")

    def test_assign_to_student_and_auto_14_day_due_date(self) -> None:
        """Öğrenci atandığında 14 günlük otomatik iade tarihi belirlendiğini ve iadede temizlendiğini doğrular."""
        today = timezone.localdate()
        self.book.assign_to_student(self.student)
        self.book.save()

        self.book.refresh_from_db()
        self.assertEqual(self.book.status, "approved")
        self.assertEqual(self.book.borrowed_by, self.student)
        self.assertEqual(self.book.borrowed_at, today)
        self.assertEqual(self.book.due_date, today + timedelta(days=14))
        self.assertTrue(self.book.borrowed)
        self.assertFalse(self.book.is_available)

        # Model clean() üzerinden sadece borrowed_by seçilerek kaydedildiğinde de otomatik doldurulmalı
        second_book = Book(
            name="Saatleri Ayarlama Enstitüsü",
            author="Ahmet Hamdi Tanpınar",
            status="returned",
            borrowed_by=self.student,
        )
        second_book.full_clean()
        second_book.save()
        self.assertEqual(second_book.status, "approved")
        self.assertEqual(second_book.borrowed_at, today)
        self.assertEqual(second_book.due_date, today + timedelta(days=14))

        # İade alındığında tüm ödünç alanları temizlenmeli
        self.book.mark_returned()
        self.book.save()
        self.book.refresh_from_db()
        self.assertEqual(self.book.status, "returned")
        self.assertIsNone(self.book.borrowed_by)
        self.assertIsNone(self.book.borrowed_at)
        self.assertIsNone(self.book.due_date)
        self.assertTrue(self.book.is_available)

    def test_due_date_before_borrowed_at_raises_validation_error(self) -> None:
        """Son iade tarihi ödünç verilme tarihinden önce olduğunda ValidationError fırlatıldığını doğrular."""
        today = timezone.localdate()
        with self.assertRaises(ValidationError):
            self.book.assign_to_student(
                self.student,
                borrowed_at=today,
                due_date=today - timedelta(days=1),
            )

        invalid_book = Book(
            name="Hatalı Tarihli Kitap",
            author="Yazar",
            status="approved",
            borrowed_by=self.student,
            borrowed_at=today,
            due_date=today - timedelta(days=2),
        )
        with self.assertRaises(ValidationError):
            invalid_book.full_clean()

    def test_database_check_constraint_enforces_consistency(self) -> None:
        """Veritabanı CheckConstraint kuralının tutarsız durum/öğrenci/tarih kayıtlarını engellediğini doğrular."""
        today = timezone.localdate()

        # 1. 'returned' durumunda borrowed_by dolu olamaz
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Book.objects.create(
                    name="Hatalı Kitap 1",
                    author="Yazar 1",
                    status="returned",
                    borrowed_by=self.student,
                )

        # 2. 'returned' durumunda due_date dolu olamaz
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Book.objects.filter(id=self.book.id).update(due_date=today)

        # 3. 'approved' durumunda borrowed_by None olamaz
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Book.objects.create(
                    name="Hatalı Kitap 2",
                    author="Yazar 2",
                    status="approved",
                    borrowed_by=None,
                    due_date=today,
                )

        # 4. 'approved' durumunda due_date None olamaz
        borrowed_book = Book.objects.create(
            name="Ödünç Kitap",
            author="Yazar",
            status="approved",
            borrowed_by=self.student,
        )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Book.objects.filter(id=borrowed_book.id).update(due_date=None)

    def test_is_overdue_property(self) -> None:
        """is_overdue özelliğinin geçmiş tarihli ödünç kitaplarda True, diğerlerinde False döndüğünü doğrular."""
        today = timezone.localdate()
        self.book.assign_to_student(
            self.student,
            borrowed_at=today - timedelta(days=20),
            due_date=today - timedelta(days=1),
        )
        self.book.save()
        self.assertTrue(self.book.is_overdue)

        self.book.due_date = today + timedelta(days=3)
        self.book.save()
        self.assertFalse(self.book.is_overdue)

        self.book.mark_returned()
        self.book.save()
        self.assertFalse(self.book.is_overdue)

    def test_production_secret_key_required_when_debug_false(self) -> None:
        """DEBUG=False ve DJANGO_SECRET_KEY='' olduğunda ImproperlyConfigured fırlatıldığını doğrular."""
        import config.settings

        try:
            with patch.dict(os.environ, {"DJANGO_DEBUG": "False", "DJANGO_SECRET_KEY": ""}):
                with self.assertRaises(ImproperlyConfigured):
                    importlib.reload(config.settings)
        finally:
            importlib.reload(config.settings)


class BookListPerformanceAndCoverValidationTests(TestCase):
    """Katalog sorgu performansı, kapak görseli doğrulamaları ve veritabanı indeks testleri."""

    def setUp(self) -> None:
        self.student = Student.objects.create(
            full_name="Performans Öğrencisi",
            student_number="5001",
            graduation_year=2028,
        )

    def test_book_list_query_count_constant(self) -> None:
        """10 ödünçte ve 5 müsait kitap varken katalog sayfalarının sabit 1 sorguda çalıştığını doğrular."""
        for i in range(10):
            Book.objects.create(
                name=f"Ödünç Kitap {i}",
                author=f"Yazar {i}",
                status="approved",
                borrowed_by=self.student,
            )
        for i in range(5):
            Book.objects.create(
                name=f"Müsait Kitap {i}",
                author=f"Yazar {i}",
                status="returned",
                borrowed_by=None,
            )

        with self.assertNumQueries(1):
            resp_search = self.client.get(reverse("book_search"))
            self.assertEqual(resp_search.status_code, 200)

        with self.assertNumQueries(1):
            resp_books = self.client.get(reverse("book_list"))
            self.assertEqual(resp_books.status_code, 200)

    def test_cover_image_size_limit_validation(self) -> None:
        """2MB'den büyük (2.5MB) kapak görselinin ValidationError fırlattığını doğrular."""
        file_size_2_5_mb = int(2.5 * 1024 * 1024)
        large_cover = SimpleUploadedFile(
            name="large_cover.jpg",
            content=b"x" * file_size_2_5_mb,
            content_type="image/jpeg",
        )
        book = Book(name="Büyük Kapaklı Kitap", author="Test Yazar", cover=large_cover)
        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_cover_image_extension_validation(self) -> None:
        """Desteklenmeyen dosya uzantısının (.sh) ValidationError fırlattığını doğrular."""
        malicious_file = SimpleUploadedFile(
            name="dangerous_script.sh",
            content=b'#!/bin/bash\necho "test"',
            content_type="text/x-shellscript",
        )
        book = Book(name="Zararlı Dosyalı Kitap", author="Test Yazar", cover=malicious_file)
        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_book_indexes_defined(self) -> None:
        """Book modelinde bileşik arama indeksi ve durum/iade tarihi indekslerinin tanımlı olduğunu doğrular."""
        index_names = [index.name for index in Book._meta.indexes]
        self.assertIn("book_name_author_idx", index_names)
        self.assertTrue(Book._meta.get_field("status").db_index)
        self.assertTrue(Book._meta.get_field("due_date").db_index)


class AdminUIDashboardTests(TestCase):
    """Yönetim paneli, Unfold SKAL Laciverti teması, gösterge paneli ve rozet testleri."""

    def setUp(self) -> None:
        self.active_student = Student.objects.create(
            full_name="Aktif Öğrenci",
            student_number="202810",
            graduation_year=2028,
        )

    def test_timezone_setting(self) -> None:
        """Zaman diliminin Europe/Istanbul olduğunu doğrular."""
        self.assertEqual(settings.TIME_ZONE, "Europe/Istanbul")

    def test_unfold_settings_customization(self) -> None:
        """UNFOLD ayarlarının light tema, SKAL Laciverti (40 36 113) ve kenar çubuğu menülerini içerdiğini doğrular."""
        unfold_conf = settings.UNFOLD
        self.assertEqual(unfold_conf.get("THEME"), "light")
        self.assertEqual(unfold_conf.get("SITE_SUBHEADER"), "Yönetim ve Takip Paneli")
        self.assertEqual(
            unfold_conf.get("DASHBOARD_CALLBACK"),
            "library.dashboard.dashboard_callback",
        )
        self.assertIn("library/css/driver.css", unfold_conf.get("STYLES", []))
        self.assertIn("library/css/admin_custom.css", unfold_conf.get("STYLES", []))
        self.assertIn("library/js/driver.js", unfold_conf.get("SCRIPTS", []))
        self.assertIn("library/js/admin_tour.js", unfold_conf.get("SCRIPTS", []))
        self.assertEqual(
            unfold_conf.get("COLORS", {}).get("primary", {}).get("600"),
            "40 36 113",
        )

        nav_items = unfold_conf["SIDEBAR"]["navigation"][0]["items"]
        nav_titles = [item["title"] for item in nav_items]
        self.assertIn("Kitap Kataloğu", nav_titles)
        self.assertIn("Öğrenciler", nav_titles)

    def test_dashboard_callback_kpis_and_auto_graduation_purge(self) -> None:
        """dashboard_callback çağrısının mezunları otomatik temizlediğini ve tüm KPI metriklerini ürettiğini doğrular."""
        today = timezone.localdate()
        graduated_free = Student.objects.create(
            full_name="Silinecek Mezun",
            student_number="202201",
            graduation_year=2022,
        )
        graduated_locked = Student.objects.create(
            full_name="Zimmetli Mezun",
            student_number="202202",
            graduation_year=2022,
        )

        Book.objects.create(name="Müsait Kitap", author="Yazar 1", status="returned")
        Book.objects.create(
            name="Zamanında Ödünç Kitap",
            author="Yazar 2",
            status="approved",
            borrowed_by=self.active_student,
            borrowed_at=today,
            due_date=today + timedelta(days=7),
        )
        Book.objects.create(
            name="Gecikmiş Mezun Kitabı",
            author="Yazar 3",
            status="approved",
            borrowed_by=graduated_locked,
            borrowed_at=today - timedelta(days=20),
            due_date=today - timedelta(days=5),
        )

        req = RequestFactory().get("/admin/")
        ctx = dashboard_callback(req, {})

        self.assertFalse(Student.objects.filter(id=graduated_free.id).exists())
        self.assertTrue(Student.objects.filter(id=graduated_locked.id).exists())

        stats = ctx["kpi_stats"]
        self.assertEqual(stats["total_books"], 3)
        self.assertEqual(stats["available_books"], 1)
        self.assertEqual(stats["approved_loans"], 2)
        self.assertEqual(stats["overdue_books"], 1)
        self.assertEqual(stats["total_students"], 2)
        self.assertEqual(stats["graduated_with_loans"], 1)
        self.assertEqual(stats["purged_graduated_count"], 1)

    def test_overdue_books_badge_behavior(self) -> None:
        """Gecikmiş kitap olmadığında rozetin None, gecikmiş kitap olduğunda sayıyı döndürdüğünü doğrular."""
        today = timezone.localdate()
        req = RequestFactory().get("/admin/")

        self.assertIsNone(overdue_books_badge(req))
        self.assertIsNone(pending_books_badge(req))

        # Gecikmemiş ödünç kitap rozeti tetiklememeli
        Book.objects.create(
            name="Normal Ödünç",
            author="Yazar",
            status="approved",
            borrowed_by=self.active_student,
            borrowed_at=today,
            due_date=today + timedelta(days=5),
        )
        self.assertIsNone(overdue_books_badge(req))

        # Gecikmiş kitap eklendiğinde '1' döndürmeli
        Book.objects.create(
            name="Gecikmiş Kitap",
            author="Yazar",
            status="approved",
            borrowed_by=self.active_student,
            borrowed_at=today - timedelta(days=15),
            due_date=today - timedelta(days=1),
        )
        self.assertEqual(overdue_books_badge(req), "1")
        self.assertEqual(pending_books_badge(req), "1")

    def test_book_and_student_admin_configuration(self) -> None:
        """BookAdmin ve StudentAdmin sınıflarının yapılandırmasını, rozetlerini ve aksiyonlarını doğrular."""
        book_admin = BookAdmin(Book, site)
        student_admin = StudentAdmin(Student, site)

        self.assertEqual(
            book_admin.list_display,
            (
                "cover_thumbnail",
                "name",
                "author",
                "status_badge",
                "borrowed_by",
                "borrowed_at",
                "due_date_badge",
            ),
        )
        self.assertEqual(book_admin.autocomplete_fields, ("borrowed_by",))
        self.assertEqual(
            student_admin.list_display,
            (
                "full_name",
                "student_number",
                "graduation_year",
                "graduation_status_badge",
                "active_loans_count",
            ),
        )

        today = timezone.localdate()
        overdue_book = Book.objects.create(
            name="Gecikmiş Rozet Kitabı",
            author="Yazar",
            status="approved",
            borrowed_by=self.active_student,
            borrowed_at=today - timedelta(days=20),
            due_date=today - timedelta(days=2),
        )
        status_key, status_label = book_admin.status_badge(overdue_book)
        self.assertEqual(status_key, "approved")
        self.assertEqual(status_label, "Ödünçte")
        self.assertIn("(Gecikti)", book_admin.due_date_badge(overdue_book))
        self.assertIn("-", str(book_admin.cover_thumbnail(overdue_book)))

        grad_key, grad_label = student_admin.graduation_status_badge(self.active_student)
        self.assertEqual(grad_key, "active")
        self.assertEqual(grad_label, "Aktif Öğrenci")
        self.assertEqual(student_admin.active_loans_count(self.active_student), 1)

        # purge_graduated_action testi
        grad_student = Student.objects.create(
            full_name="Aksiyonla Silinecek",
            student_number="202199",
            graduation_year=2021,
        )
        mock_admin = MockModelAdmin()
        purge_graduated_action(
            mock_admin,
            RequestFactory().post("/admin/library/student/"),
            Student.objects.all(),
        )
        self.assertFalse(Student.objects.filter(id=grad_student.id).exists())


class StaticLogoAssetsTests(TestCase):
    """Optimize edilmiş şeffaf arka planlı 6 adet SKAL logo ve ikon varlığını doğrular."""

    def test_all_six_logo_assets_exist_and_have_transparent_corners(self) -> None:
        img_dir = Path(settings.BASE_DIR) / "library" / "static" / "library" / "img"
        expected_files = [
            "logo.png",
            "logo.webp",
            "logo-sm.png",
            "logo-lg.png",
            "favicon-32x32.png",
            "apple-touch-icon.png",
        ]
        for filename in expected_files:
            file_path = img_dir / filename
            with self.subTest(filename=filename):
                self.assertTrue(file_path.exists(), f"{filename} bulunamadı.")
                self.assertGreater(file_path.stat().st_size, 0)
                with Image.open(file_path) as img:
                    rgba = img.convert("RGBA")
                    self.assertEqual(
                        rgba.getpixel((0, 0))[3],
                        0,
                        f"{filename} sol üst köşesi şeffaf (alpha=0) olmalıdır.",
                    )
