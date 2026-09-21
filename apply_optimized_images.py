from pathlib import Path
import shutil

PROJECT_DIR = Path(__file__).resolve().parent
IMAGE_DIR = PROJECT_DIR / "images"
OPTIMIZED_DIR = IMAGE_DIR / "optimized"
BACKUP_DIR = IMAGE_DIR / "original-backup"

SUPPORTED_FORMATS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


def format_size(size):
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.2f} MB"


def main():

    if not OPTIMIZED_DIR.exists():
        print("ERROR: optimized folder not found.")
        return

    BACKUP_DIR.mkdir(exist_ok=True)

    replaced = 0
    skipped = 0

    print()
    print("=" * 75)
    print("ROSHXLAB — APPLY OPTIMIZED IMAGES")
    print("=" * 75)
    print()

    for optimized in sorted(OPTIMIZED_DIR.rglob("*")):

        if not optimized.is_file():
            continue

        if optimized.suffix.lower() not in SUPPORTED_FORMATS:
            continue

        relative = optimized.relative_to(OPTIMIZED_DIR)

        original = IMAGE_DIR / relative
        backup = BACKUP_DIR / relative

        if not original.exists():
            print(f"SKIPPED: {relative} -> original not found")
            skipped += 1
            continue

        original_size = original.stat().st_size
        optimized_size = optimized.stat().st_size

        # Never replace with a larger file.
        if optimized_size >= original_size:
            print(
                f"SKIPPED: {relative} "
                f"(optimized file is not smaller)"
            )
            skipped += 1
            continue

        # Backup original.
        backup.parent.mkdir(parents=True, exist_ok=True)

        if not backup.exists():
            shutil.copy2(original, backup)

        # Replace original.
        shutil.copy2(optimized, original)

        reduction = (
            (original_size - optimized_size)
            / original_size
        ) * 100

        print(
            f"REPLACED: {relative}"
            f"\n          {format_size(original_size)}"
            f" -> {format_size(optimized_size)}"
            f" ({reduction:.1f}% smaller)"
        )

        replaced += 1

    print()
    print("=" * 75)
    print(f"Images replaced: {replaced}")
    print(f"Images skipped:  {skipped}")
    print("=" * 75)
    print()
    print("Original images are backed up in:")
    print(BACKUP_DIR)
    print()


if __name__ == "__main__":
    main()