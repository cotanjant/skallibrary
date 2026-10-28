"""
SKAL Kütüphanesi - Yönetim Paneli Gösterge Paneli ve Rozet Geri Çağrıları.

Bu modül, Django Unfold yönetim arayüzü için dinamik KPI istatistiklerini,
mezun öğrenci otomatik temizliğini, son hareketleri ve kenar çubuğundaki
(sidebar) gecikmiş kitap bildirim rozetlerini üretir.
"""

from typing import Any
from django.http import HttpRequest
from django.utils import timezone
from library.models import Book, Student


def overdue_books_badge(request: HttpRequest) -> str | None:
    """Kenar çubuğunda kitap kataloğu için gecikmiş iade rozetini üretir."""
    today = timezone.localdate()
    count = Book.objects.filter(status='approved', due_date__lt=today).count()
    return str(count) if count > 0 else None


pending_books_badge = overdue_books_badge


def dashboard_callback(request: HttpRequest, context: dict[str, Any]) -> dict[str, Any]:
    """Django Unfold ana gösterge paneli için gerçek veriye dayalı KPI ve hareket verilerini hazırlar."""
    purged_count, graduated_with_loans = Student.purge_graduated()
    today = timezone.localdate()

    total_books: int = Book.objects.count()
    available_books: int = Book.objects.filter(
        status='returned',
        borrowed_by__isnull=True,
    ).count()
    approved_loans: int = Book.objects.filter(status='approved').count()
    overdue_books: int = Book.objects.filter(status='approved', due_date__lt=today).count()
    total_students: int = Student.objects.count()

    recent_loans: list[Book] = list(
        Book.objects.select_related('borrowed_by').all()[:5]
    )

    kpi_stats: dict[str, int] = {
        "total_books": total_books,
        "available_books": available_books,
        "approved_loans": approved_loans,
        "overdue_books": overdue_books,
        "total_students": total_students,
        "graduated_with_loans": graduated_with_loans,
        "purged_graduated_count": purged_count,
    }

    kpi_cards: list[dict[str, Any]] = [
        {
            "title": "Toplam Kitap",
            "metric": total_books,
            "icon": "auto_stories",
            "description": "Kütüphanede kayıtlı toplam kitap sayısı",
        },
        {
            "title": "Müsait Kitaplar",
            "metric": available_books,
            "icon": "check_circle",
            "description": "Ödünç verilmeye hazır kitaplar",
        },
        {
            "title": "Ödünçteki Kitaplar",
            "metric": approved_loans,
            "icon": "person_pin",
            "description": "Öğrencilerde bulunan aktif kitaplar",
        },
        {
            "title": "Gecikmiş İadeler",
            "metric": overdue_books,
            "icon": "warning",
            "description": "Son iade tarihi geçmiş kitaplar",
        },
        {
            "title": "Kayıtlı Öğrenciler",
            "metric": total_students,
            "icon": "school",
            "description": "Sistemde kayıtlı aktif öğrenci sayısı",
        },
        {
            "title": "Zimmetli Mezunlar",
            "metric": graduated_with_loans,
            "icon": "lock_person",
            "description": "Kitap iadesi beklenen mezun öğrenciler",
        },
    ]

    context.update({
        "kpi_stats": kpi_stats,
        "kpi_cards": kpi_cards,
        "recent_loans": recent_loans,
        "recent_books": recent_loans,
        "purged_graduated_count": purged_count,
        "graduated_with_loans": graduated_with_loans,
    })

    return context
