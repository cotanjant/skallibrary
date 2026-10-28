from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from library.models import Book


def home(req: HttpRequest) -> HttpResponse:
    """Kütüphane karşılama sayfasını istatistikler ve öne çıkan kitaplarla görüntüler."""
    stats = Book.objects.aggregate(
        total_books=Count('id'),
        available_books=Count('id', filter=Q(status='returned', borrowed_by__isnull=True)),
        borrowed_books=Count('id', filter=Q(status='approved')),
    )
    featured_books = list(
        Book.objects.only('id', 'name', 'author', 'cover', 'status', 'due_date', 'borrowed_by_id')
        .order_by('-status', 'name')[:6]
    )
    return render(
        req,
        "library/home.html",
        {
            "total_books": stats["total_books"] or 0,
            "available_books": stats["available_books"] or 0,
            "borrowed_books": stats["borrowed_books"] or 0,
            "featured_books": featured_books,
        },
    )


def book_list(req: HttpRequest) -> HttpResponse:
    """Kitap kataloğunu arama, durum filtresi ve sıralama seçenekleriyle tek sorguda listeler."""
    q = req.GET.get('q', '').strip()
    status_filter = req.GET.get('status', '').strip()
    sort = req.GET.get('sort', 'name').strip()

    queryset = Book.objects.select_related('borrowed_by')

    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(author__icontains=q))

    if status_filter == 'available':
        queryset = queryset.filter(status='returned')
    elif status_filter == 'borrowed':
        queryset = queryset.filter(status='approved')
    else:
        status_filter = ''

    sort_map: dict[str, tuple[str, ...]] = {
        'name': ('name',),
        'author': ('author', 'name'),
        'availability': ('-status', 'name'),
        'due_date': ('due_date', 'name'),
    }
    if sort not in sort_map:
        sort = 'name'
    queryset = queryset.order_by(*sort_map[sort])

    books = list(queryset)
    total_count = len(books)
    available_count = sum(1 for b in books if b.is_available)
    borrowed_count = sum(1 for b in books if b.borrowed)

    return render(
        req,
        "library/books.html",
        {
            "books": books,
            "query": q,
            "current_status": status_filter,
            "current_sort": sort,
            "total_books": total_count,
            "available_books": available_count,
            "borrowed_books": borrowed_count,
            "total_count": total_count,
            "available_count": available_count,
            "borrowed_count": borrowed_count,
        },
    )
