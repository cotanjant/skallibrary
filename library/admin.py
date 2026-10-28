from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import SafeText, mark_safe
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from library.models import Book, Student

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.action(description="Mezun öğrencileri temizle (Zimmetsiz olanlar)")
def purge_graduated_action(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    """Mezuniyet yılı geçmiş ve üzerinde ödünç kitap bulunmayan öğrencileri siler."""
    deleted_count, blocked_count = Student.purge_graduated()
    modeladmin.message_user(
        request,
        f"{deleted_count} mezun öğrenci kaydı silindi. "
        f"Zimmetli kitabı bulunan {blocked_count} mezun öğrenci korundu.",
    )


@admin.register(Student)
class StudentAdmin(ModelAdmin):
    list_display = (
        'full_name',
        'student_number',
        'graduation_year',
        'graduation_status_badge',
        'active_loans_count',
    )
    list_filter = ('graduation_year',)
    list_filter_submit = True
    search_fields = ('full_name', 'student_number')
    search_help_text = "Öğrenci adı veya okul numarasına göre arama yapabilirsiniz."
    list_per_page = 20
    actions = [purge_graduated_action]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(loans_count=Count('borrowed_books'))

    @display(
        description="Mezuniyet Durumu",
        label={
            'graduated': 'warning',
            'active': 'success',
        },
    )
    def graduation_status_badge(self, obj: Student) -> tuple[str, str]:
        """Öğrencinin aktif veya mezun durumunu rozet olarak görüntüler."""
        if obj.is_graduated:
            return 'graduated', 'Mezun'
        return 'active', 'Aktif Öğrenci'

    @display(description="Zimmetli Kitap")
    def active_loans_count(self, obj: Student) -> int:
        """Öğrencinin üzerindeki aktif ödünç kitap sayısını döndürür."""
        return getattr(obj, 'loans_count', obj.borrowed_books.count())


@admin.action(description="Seçili kitapları iade al (Müsait yap)")
def mark_books_returned(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    """Seçili ödünçteki kitapların iadesini alır ve mezun öğrencileri kontrol eder."""
    count = 0
    with transaction.atomic():
        for book in queryset.filter(status='approved'):
            book.mark_returned()
            book.save()
            count += 1
        purged_count, _ = Student.purge_graduated()

    msg = f"{count} adet kitap iade alındı ve müsait duruma getirildi."
    if purged_count > 0:
        msg += f" Zimmeti kalmayan {purged_count} mezun öğrenci kaydı otomatik temizlendi."
    modeladmin.message_user(request, msg)


@admin.register(Book)
class BookAdmin(ModelAdmin):
    list_display = (
        'cover_thumbnail',
        'name',
        'author',
        'status_badge',
        'borrowed_by',
        'borrowed_at',
        'due_date_badge',
    )
    list_filter = ('status', 'due_date')
    list_filter_submit = True
    search_fields = (
        'name',
        'author',
        'borrowed_by__full_name',
        'borrowed_by__student_number',
    )
    search_help_text = "Kitap adı, yazar, öğrenci adı veya okul numarasına göre arama yapabilirsiniz."
    autocomplete_fields = ('borrowed_by',)
    list_per_page = 20
    actions = [mark_books_returned]

    @display(description="Kapak", image=True)
    def cover_thumbnail(self, obj: Book) -> SafeText:
        """Kitabın kapak görselinin küçük önizlemesini görüntüler."""
        if obj.cover:
            return format_html(
                '<img src="{}" class="h-10 w-8 object-cover rounded shadow-xs" alt="{}">',
                obj.cover.url,
                obj.name,
            )
        return mark_safe('<span class="text-base-400 text-xs">-</span>')

    @display(
        description="Durum",
        label={
            'approved': 'warning',
            'returned': 'success',
        },
    )
    def status_badge(self, obj: Book) -> tuple[str, str]:
        """Kitabın ödünç ve müsaitlik durumunu renkli durum rozeti olarak görüntüler."""
        status_labels = {
            'approved': 'Ödünçte',
            'returned': 'Müsait',
        }
        return obj.status, status_labels.get(obj.status, obj.get_status_display())

    @display(description="Son İade Tarihi")
    def due_date_badge(self, obj: Book) -> str:
        """Kitabın son iade tarihini ve gecikme durumunu görüntüler."""
        if not obj.due_date:
            return "-"
        formatted = obj.due_date.strftime("%d.%m.%Y")
        if obj.is_overdue:
            return f"{formatted} (Gecikti)"
        return formatted
