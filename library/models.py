from datetime import date, timedelta
import uuid
from typing import Any
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone


def validate_cover_image(value: Any) -> None:
    """Kapak görselinin maksimum 2MB boyutunda olmasını doğrular."""
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError("Kapak görseli maksimum 2MB boyutunda olabilir.")


class Student(models.Model):
    """Kütüphaneden kitap ödünç alabilen okul öğrencilerini temsil eder."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Kimlik",
    )
    full_name = models.CharField(max_length=255, verbose_name="Ad Soyad")
    student_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Okul Numarası",
    )
    graduation_year = models.PositiveIntegerField(
        db_index=True,
        verbose_name="Mezuniyet Yılı",
        validators=[MinValueValidator(2020), MaxValueValidator(2100)],
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")

    class Meta:
        verbose_name = "Öğrenci"
        verbose_name_plural = "Öğrenciler"
        ordering = ['graduation_year', 'full_name']

    @classmethod
    def current_graduation_cutoff_year(cls, today: date | None = None) -> int:
        """Akademik takvime göre (1 Temmuz itibarıyla) mezuniyet sınır yılını hesaplar."""
        today = today or timezone.localdate()
        if (today.month, today.day) >= (7, 1):
            return today.year
        return today.year - 1

    @property
    def is_graduated(self) -> bool:
        """Öğrencinin mezuniyet yılının dolup dolmadığını belirtir."""
        return self.graduation_year <= self.current_graduation_cutoff_year()

    @classmethod
    def purge_graduated(cls, today: date | None = None) -> tuple[int, int]:
        """Mezuniyet yılı geçmiş ve üzerinde zimmetli kitap bulunmayan öğrencileri siler.

        Zimmet Kilidi: Üzerinde ödünç kitap bulunan mezun öğrenciler silinmez.

        Returns:
            tuple[int, int]: (silinen_ogrenci_sayisi, zimmet_nedeniyle_korunan_mezun_sayisi)
        """
        cutoff = cls.current_graduation_cutoff_year(today)
        with transaction.atomic():
            graduated_qs = cls.objects.filter(graduation_year__lte=cutoff)
            blocked_count = graduated_qs.filter(borrowed_books__isnull=False).distinct().count()
            deletable_qs = graduated_qs.filter(borrowed_books__isnull=True)
            deleted_count, _ = deletable_qs.delete()
        return deleted_count, blocked_count

    def __str__(self) -> str:
        return f"{self.full_name} ({self.student_number} - Mezuniyet: {self.graduation_year})"


class Book(models.Model):
    STATUS_CHOICES = (
        ('returned', 'Müsait'),
        ('approved', 'Ödünçte'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Kimlik",
    )
    name = models.CharField(max_length=255, verbose_name="Kitap Adı")
    author = models.CharField(max_length=255, verbose_name="Yazar")
    cover = models.ImageField(
        upload_to='covers/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_cover_image,
        ],
        verbose_name="Kapak Resmi",
    )
    borrowed_by = models.ForeignKey(
        'library.Student',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="borrowed_books",
        verbose_name="Ödünç Alan Öğrenci",
    )
    borrowed_at = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ödünç Verilme Tarihi",
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Son İade Tarihi",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='returned',
        db_index=True,
        verbose_name="Durum",
    )

    class Meta:
        verbose_name = "Kitap"
        verbose_name_plural = "Kitaplar"
        indexes = [
            models.Index(fields=['name', 'author'], name='book_name_author_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    (
                        models.Q(status='approved')
                        & models.Q(borrowed_by__isnull=False)
                        & models.Q(due_date__isnull=False)
                    )
                    | (
                        models.Q(status='returned')
                        & models.Q(borrowed_by__isnull=True)
                        & models.Q(due_date__isnull=True)
                    )
                ),
                name="book_status_borrower_consistency",
            )
        ]

    def assign_to_student(
        self,
        student: Student,
        borrowed_at: date | None = None,
        due_date: date | None = None,
    ) -> None:
        """Kitabı belirtilen öğrenciye ödünç verir ve iade tarihini (varsayılan 14 gün) atar."""
        if student is None:
            raise ValidationError("Ödünç verilecek öğrenci seçilmelidir.")
        actual_borrowed_at = borrowed_at or timezone.localdate()
        actual_due_date = due_date or (actual_borrowed_at + timedelta(days=14))
        if actual_due_date < actual_borrowed_at:
            raise ValidationError("Son iade tarihi, ödünç verilme tarihinden önce olamaz.")
        self.borrowed_by = student
        self.status = 'approved'
        self.borrowed_at = actual_borrowed_at
        self.due_date = actual_due_date

    def mark_returned(self) -> None:
        """Kitabın iadesini alır ve tekrar müsait duruma getirir."""
        self.status = 'returned'
        self.borrowed_by = None
        self.borrowed_at = None
        self.due_date = None

    def clean(self) -> None:
        """Yönetim paneli ve model doğrulamalarında durum-öğrenci-tarih senkronizasyonunu sağlar."""
        super().clean()
        if self.borrowed_by is not None and self.status == 'returned':
            self.status = 'approved'

        if self.status == 'approved':
            if self.borrowed_by is None:
                raise ValidationError({'borrowed_by': 'Ödünç verilen kitap için bir öğrenci seçilmelidir.'})
            if self.borrowed_at is None:
                self.borrowed_at = timezone.localdate()
            if self.due_date is None:
                self.due_date = self.borrowed_at + timedelta(days=14)
            if self.due_date < self.borrowed_at:
                raise ValidationError({'due_date': 'Son iade tarihi, ödünç verilme tarihinden önce olamaz.'})
        elif self.status == 'returned' and self.borrowed_by is None:
            self.borrowed_at = None
            self.due_date = None

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Kayıt sırasında ödünç ve iade tarihlerini otomatik senkronize eder."""
        if self.status == 'approved' and self.borrowed_by is not None:
            if self.borrowed_at is None:
                self.borrowed_at = timezone.localdate()
            if self.due_date is None:
                self.due_date = self.borrowed_at + timedelta(days=14)
        elif self.status == 'returned' and self.borrowed_by is None:
            self.borrowed_at = None
            self.due_date = None
        super().save(*args, **kwargs)

    @property
    def borrowed(self) -> bool:
        """Kitabın şu anda ödünçte olup olmadığını belirtir."""
        return self.status == 'approved'

    @property
    def is_available(self) -> bool:
        """Kitabın ödünç verilmeye müsait olup olmadığını belirtir."""
        return self.status == 'returned' and self.borrowed_by_id is None

    @property
    def is_overdue(self) -> bool:
        """Ödünçteki kitabın son iade tarihinin geçip geçmediğini belirtir."""
        return bool(self.borrowed and self.due_date and self.due_date < timezone.localdate())

    def __str__(self) -> str:
        """Kitabın adını ve yazarını gösteren metin temsilini döndürür."""
        return f"{self.name} - {self.author}"
