from typing import Any
from django.core.management.base import BaseCommand
from library.models import Student


class Command(BaseCommand):
    help = "Mezuniyet yılı geçmiş ve üzerinde zimmetli kitap bulunmayan öğrencileri otomatik olarak siler."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Silme işlemi yapmadan kaç mezun öğrencinin silineceğini ve korunacağını gösterir.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if options.get("dry_run"):
            cutoff = Student.current_graduation_cutoff_year()
            graduated_qs = Student.objects.filter(graduation_year__lte=cutoff)
            deletable_count = graduated_qs.filter(borrowed_books__isnull=True).distinct().count()
            blocked_count = graduated_qs.filter(borrowed_books__isnull=False).distinct().count()
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY-RUN] {deletable_count} mezun öğrenci silinecek, "
                    f"zimmetli kitabı bulunan {blocked_count} mezun öğrenci korunacak."
                )
            )
            return

        deleted_count, blocked_count = Student.purge_graduated()
        self.stdout.write(
            self.style.SUCCESS(
                f"{deleted_count} mezun öğrenci kaydı silindi. "
                f"Zimmetli kitabı bulunan {blocked_count} mezun öğrenci korundu."
            )
        )
