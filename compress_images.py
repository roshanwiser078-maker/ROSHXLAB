from pathlib import Path
from PIL import Image

PROJECT_DIR = Path(__file__).resolve().parent
IMAGE_DIR = PROJECT_DIR / "images"
OUTPUT_DIR = IMAGE_DIR / "optimized"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_FORMATS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

JPEG_QUALITY = 82
WEBP_QUALITY = 82
PNG_COMPRESS_LEVEL = 9


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"

    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"

    return f"{size_bytes / (1024 * 1024):.2f} MB"


def optimize_image(source):

    relative_path = source.relative_to(IMAGE_DIR)
    destination = OUTPUT_DIR / relative_path

    destination.parent.mkdir(parents=True, exist_ok=True)

    try:

        with Image.open(source) as img:

            original_size = source.stat().st_size
            extension = source.suffix.lower()

            # ---------------------------------
            # JPEG / JPG
            # ---------------------------------

            if extension in (".jpg", ".jpeg"):

                # JPEG cannot store transparency.
                # Put transparent areas on a dark background.
                if img.mode in ("RGBA", "LA", "P"):

                    rgba = img.convert("RGBA")

                    background = Image.new(
                        "RGB",
                        rgba.size,
                        (7, 9, 8)
                    )

                    background.paste(
                        rgba,
                        mask=rgba.getchannel("A")
                    )

                    working = background

                else:
                    working = img.convert("RGB")

                working.save(
                    destination,
                    format="JPEG",
                    quality=JPEG_QUALITY,
                    optimize=True,
                    progressive=True
                )

            # ---------------------------------
            # WEBP
            # ---------------------------------

            elif extension == ".webp":

                if img.mode in ("RGBA", "LA"):
                    working = img.convert("RGBA")
                else:
                    working = img.convert("RGB")

                working.save(
                    destination,
                    format="WEBP",
                    quality=WEBP_QUALITY,
                    method=6
                )

            # ---------------------------------
            # PNG
            # ---------------------------------

            elif extension == ".png":

                # Preserve transparency.
                if img.mode in ("RGBA", "LA", "P"):

                    working = img.convert("RGBA")

                else:

                    working = img.convert("RGB")

                working.save(
                    destination,
                    format="PNG",
                    optimize=True,
                    compress_level=PNG_COMPRESS_LEVEL
                )

            optimized_size = destination.stat().st_size

            # ---------------------------------
            # If optimization made the file
            # larger, keep the original instead.
            # ---------------------------------

            if optimized_size >= original_size:

                destination.unlink()

                print(
                    f"SKIPPED: {source.name:32} "
                    f"original {format_size(original_size):>10} "
                    f"(optimized version was larger)"
                )

                return

            reduction = (
                (original_size - optimized_size)
                / original_size
            ) * 100

            print(
                f"OK:      {source.name:32} "
                f"{format_size(original_size):>10} -> "
                f"{format_size(optimized_size):>10} "
                f"({reduction:5.1f}% smaller)"
            )

    except Exception as error:

        print(
            f"ERROR:   {source.name:32} -> {error}"
        )


def main():

    if not IMAGE_DIR.exists():

        print("ERROR: images folder not found.")
        return

    print()
    print("=" * 78)
    print("ROSHXLAB IMAGE OPTIMIZER")
    print("=" * 78)
    print()

    images = [
        file
        for file in IMAGE_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in SUPPORTED_FORMATS
    ]

    if not images:

        print("No supported images found.")
        return

    print(f"Found {len(images)} images.")
    print()
    print("Creating optimized copies...")
    print()

    for image in sorted(images):

        optimize_image(image)

    print()
    print("=" * 78)
    print("DONE")
    print("=" * 78)
    print()
    print(f"Optimized folder:")
    print(OUTPUT_DIR)
    print()
    print("Original images were NOT changed.")
    print()


if __name__ == "__main__":
    main()