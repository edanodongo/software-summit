"""
Batch Badge Generator Script - Integrated Version
Processes registrants in batches, generates badges using build_exhibitor_badge_pdf,
organizes by category, and updates print status.
 python manage.py shell -c "from badge_gen import process_all_badges; process_all_badges(batch_size=10)"
python manage.py shell -c "from badge_gen import process_all_badges; process_all_badges(batch_size=10)"

Usage:
    python manage.py shell
    >>> from summitPage.badge_batch_processor import process_all_badges
    >>> process_all_badges(batch_size=10)
"""

import math
import os
import logging
from io import BytesIO
from django.conf import settings
from django.db import transaction
from reportlab.lib.pagesizes import A8
from reportlab.platypus import Image as PlatypusImage
from summitPage.models import Registrant, Category
from PIL import ImageDraw, Image
import qrcode
from django.core.files.storage import default_storage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait, A7
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

# Enable PDF compression globally
import reportlab.rl_config
reportlab.rl_config.defaultPageCompression = 1
reportlab.rl_config.pageCompression = 1

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_category_folder_path(category_name):
    """
    Get or create the folder path for a specific category.

    Args:
        category_name (str): Name of the category

    Returns:
        str: Full path to the category folder
    """
    base_dir = os.path.join(settings.MEDIA_ROOT, "categories")
    os.makedirs(base_dir, exist_ok=True)

    # Clean up folder name (safe for filesystem)
    folder_name = category_name.strip().replace(" ", "_").replace("/", "_").lower()
    folder_path = os.path.join(base_dir, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger.info(f"✅ Created category folder: {folder_path}")

    return folder_path


def build_exhibitor_badge_pdf(exhib, page_size=portrait(A8)):
    """
    Generate a badge PDF for an exhibitor/registrant.
    Returns a BytesIO buffer containing the PDF.
    OPTIMIZED: Cleans up resources after generation.
    """
    pdf_buffer = None
    qr_buffer = None

    try:
        category_obj = Category.objects.only("name", "color").get(id=exhib.category)
        badge_color = category_obj.color or colors.black
    except Category.DoesNotExist:
        logger.error(f"Category not found for registrant {exhib.id}")
        badge_color = colors.black

    # --- Core Data ---
    full_name = exhib.get_full_name() or ""
    national_id = exhib.national_id_number or ""
    org_type = exhib.display_org_type() or ""
    job_title = exhib.job_title or ""
    category = exhib.get_category_display() or ""

    # --- Generate QR Code ---
    qr_data = (
        f"Name: {full_name}\n"
        f"National ID/ Passport NO: {national_id}\n"
        f"Organization: {org_type}\n"
        f"Job Title: {job_title}\n"
        f"Category: {category}\n"
    )
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)

    # --- PDF Setup (ONLY ONCE) ---
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=page_size)
    width, height = page_size

    # --- Scale constants based on size ---
    base_width, base_height = portrait(A7)
    scale_w = width / base_width
    scale_h = height / base_height
    scale = (scale_w + scale_h) / 2

    def s(val):
        return val * scale

    ###############################################################
    # ======================== PAGE 1 =============================
    ###############################################################

    # --- Background ---
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # --- Flag accents ---
    def draw_accent_shapes():
        c.setFillColor(colors.HexColor("#3aa655"))
        path = c.beginPath()
        path.moveTo(width * 0.68, height * 0.18)
        path.lineTo(width * 0.83, height * 0.28)
        path.lineTo(width * 0.68, height * 0.36)
        path.close()
        c.drawPath(path, fill=1, stroke=0)

        offset = s(45)
        c.setStrokeColor("#d62612")
        c.setLineWidth(s(0.5))
        c.line(width * 0.5 - offset, 0, width - offset, height * 0.35)

        c.setFillColor(badge_color)
        path = c.beginPath()
        path.moveTo(0, 0)
        path.lineTo(width * 0.8, 0)
        path.lineTo(0, height * 0.4)
        path.close()
        c.drawPath(path, fill=1, stroke=0)

        c.setFillColor(colors.HexColor("#d62612"))
        path = c.beginPath()
        path.moveTo(width, 0)
        path.lineTo(width, height * 0.35)
        path.lineTo(width * 0.5, 0)
        path.close()
        c.drawPath(path, fill=1, stroke=0)

    draw_accent_shapes()

    # --- Summit Logos ---
    summit_logo_path = os.path.join(settings.BASE_DIR, "static", "images", "summit_logo.png")
    partner_logo_path = os.path.join(settings.BASE_DIR, "static", "images", "badge_partner.png")

    margin_x = width * 0.05
    margin_top = height * 0.06

    logo_h = height * 0.25
    spacing = width * 0.01
    total_width = 0
    images = []

    if os.path.exists(partner_logo_path):
        img = ImageReader(partner_logo_path)
        w = width * 0.48
        images.append((img, w))
        total_width += w

    if os.path.exists(summit_logo_path):
        if images:
            total_width += spacing
        img = ImageReader(summit_logo_path)
        w = width * 0.52
        images.append((img, w))
        total_width += w

    if images:
        start_x = (width - total_width) / 2
        y_pos = height - margin_top - logo_h
        for img, w in images:
            c.drawImage(img, start_x, y_pos, width=w, height=logo_h,
                        preserveAspectRatio=True, mask="auto")
            start_x += w + spacing

    # --- Passport Photo ---
    photo_w, photo_h = 65, 65
    photo_x, photo_y = (width - photo_w) / 2, height - 120

    def draw_placeholder():
        """Draw placeholder image from static folder"""
        placeholder_path = os.path.join(settings.BASE_DIR, "static", "images", "speakers", "placeholder.jpg")

        if os.path.exists(placeholder_path):
            try:
                # Use the actual placeholder image
                img = Image.open(placeholder_path).convert("RGBA")
                img = img.point(lambda p: p * 1.03)

                # Resize to double for better quality
                img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)

                # Crop to square (same logic as passport photo)
                min_side = min(img.size)
                offset = int(min_side * 0.10)
                left = (img.width - min_side) / 2
                top = max((img.height - min_side) / 2 - offset, 0)
                img = img.crop((left, top, left + min_side, top + min_side))
                img = img.resize((photo_w * 2, photo_h * 2), Image.LANCZOS)

                # Create circular mask
                mask = Image.new("L", img.size, 0)
                ImageDraw.Draw(mask).ellipse((0, 0, img.size[0], img.size[1]), fill=255)

                circ = Image.new("RGBA", img.size)
                circ.paste(img, (0, 0), mask=mask)

                buf = BytesIO()
                circ.save(buf, format="PNG")
                buf.seek(0)

                c.drawImage(ImageReader(buf), photo_x, photo_y,
                            width=photo_w, height=photo_h, mask="auto")

                # Draw borders
                center_x = width / 2
                center_y = photo_y + photo_h / 2

                c.setLineWidth(1.6)
                c.setStrokeColor(colors.white)
                c.circle(center_x, center_y, (photo_w / 2) + 1)

                c.setLineWidth(0.8)
                c.setStrokeColor(colors.HexColor("#3aa655"))
                c.circle(center_x, center_y, (photo_w / 2) + 2)

                buf.close()

            except Exception as e:
                logger.warning(f"Error loading placeholder image: {str(e)}")
                # Fallback to grey rectangle if placeholder fails
                c.setFillColor(colors.lightgrey)
                c.roundRect(photo_x, photo_y, photo_w, photo_h, 6, fill=1)
                c.setFillColor(colors.darkgrey)
                c.setFont("Helvetica", 6)
                c.drawCentredString(width / 2, photo_y + photo_h / 2 - 2, "No Photo")
        else:
            # Fallback if placeholder.jpg doesn't exist
            logger.warning(f"Placeholder image not found at: {placeholder_path}")
            c.setFillColor(colors.lightgrey)
            c.roundRect(photo_x, photo_y, photo_w, photo_h, 6, fill=1)
            c.setFillColor(colors.darkgrey)
            c.setFont("Helvetica", 6)
            c.drawCentredString(width / 2, photo_y + photo_h / 2 - 2, "No Photo")

    def draw_passport():
        try:
            if not (exhib.passport_photo and default_storage.exists(exhib.passport_photo.name)):
                return draw_placeholder()

            photo_path = default_storage.path(exhib.passport_photo.name)
            img = Image.open(photo_path).convert("RGBA")
            img = img.point(lambda p: p * 1.03)
            img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)

            min_side = min(img.size)
            offset = int(min_side * 0.10)
            left = (img.width - min_side) / 2
            top = max((img.height - min_side) / 2 - offset, 0)
            img = img.crop((left, top, left + min_side, top + min_side))
            img = img.resize((photo_w * 2, photo_h * 2), Image.LANCZOS)

            mask = Image.new("L", img.size, 0)
            ImageDraw.Draw(mask).ellipse((0, 0, img.size[0], img.size[1]), fill=255)

            circ = Image.new("RGBA", img.size)
            circ.paste(img, (0, 0), mask=mask)

            buf = BytesIO()
            circ.save(buf, format="PNG")
            buf.seek(0)

            c.drawImage(ImageReader(buf), photo_x, photo_y,
                        width=photo_w, height=photo_h, mask="auto")

            center_x = width / 2
            center_y = photo_y + photo_h / 2

            c.setLineWidth(1.6)
            c.setStrokeColor(colors.white)
            c.circle(center_x, center_y, (photo_w / 2) + 1)

            c.setLineWidth(0.8)
            c.setStrokeColor(colors.HexColor("#3aa655"))
            c.circle(center_x, center_y, (photo_w / 2) + 2)

            buf.close()

        except Exception as e:
            logger.warning(f"Error drawing passport photo for {exhib.id}: {str(e)}")
            draw_placeholder()

    draw_passport()

    # --- Registrant Info ---
    text_y = photo_y - s(12)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", s(8.5))
    c.drawCentredString(width / 2, text_y, full_name[:35])

    c.setFont("Helvetica-Bold", s(13))
    c.drawCentredString(width / 2, text_y - s(11), category[:35])

    c.setFillColor(colors.white)
    # Define fonts and sizes
    base_font = "Helvetica-Bold"
    base_size = s(20)
    sup_size = s(12)
    text_main1, text_sup1 = "10", "th"
    text_main2, text_sup2 = "12", "th"
    dash = "–"

    # Measure total width for centering
    w_main1 = c.stringWidth(text_main1, base_font, base_size)
    w_sup1 = c.stringWidth(text_sup1, base_font, sup_size)
    w_dash = c.stringWidth(dash, base_font, base_size)
    w_main2 = c.stringWidth(text_main2, base_font, base_size)
    w_sup2 = c.stringWidth(text_sup2, base_font, sup_size)
    total_width = w_main1 + w_sup1 + w_dash + w_main2 + w_sup2

    x_start = (width / 4.3) - (total_width / 2)
    y_base = s(40)

    # Draw "10"
    c.setFont(base_font, base_size)
    c.drawString(x_start, y_base, text_main1)
    x_start += w_main1

    # Superscript "th"
    c.setFont(base_font, sup_size)
    c.drawString(x_start, y_base + s(7), text_sup1)
    x_start += w_sup1

    # Dash
    c.setFont(base_font, base_size)
    c.drawString(x_start, y_base, dash)
    x_start += w_dash

    # "12"
    c.drawString(x_start, y_base, text_main2)
    x_start += w_main2

    # Superscript "th"
    c.setFont(base_font, sup_size)
    c.drawString(x_start, y_base + s(7), text_sup2)

    # --- Date text ("November 2025") ---
    text = "November 2025"
    text_x = width / 4.2
    text_y = s(30)
    c.setFont("Helvetica", s(11))
    c.drawCentredString(text_x, text_y, text)

    # Underline accent
    text_width = c.stringWidth(text, "Helvetica", s(11))
    c.setLineWidth(s(0.6))
    c.setStrokeColor(colors.white)
    c.line(text_x - text_width / 2, text_y - s(3), text_x + text_width / 2, text_y - s(3))

    # --- Venue line ---
    c.setFont("Helvetica", s(6))
    c.drawCentredString(width / 4, s(20), "Moi University Annex Campus, ")
    c.drawCentredString(width / 6.8, s(12), "Eldoret Kenya, ")

    # --- QR Code ---
    qr_size, qr_margin = s(40), s(7)
    c.drawImage(
        qr_reader,
        width - qr_size - qr_margin,
        qr_margin,
        width=qr_size,
        height=qr_size,
        mask="auto"
    )

    c.showPage()

    ###############################################################
    # ======================== PAGE 2 =============================
    ###############################################################

    # --- Background ---
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, fill=1)

    # --- Summit Logos again ---
    summit_logo_path = os.path.join(settings.BASE_DIR, "static", "images", "electronic_citizen_solutions.png")
    partner_logo_path = os.path.join(settings.BASE_DIR, "static", "images", "Huawei_logo.png")

    logo_h = height * 0.10
    total_width = 0
    spacing = width * 0.003
    images = []

    if os.path.exists(partner_logo_path):
        img = ImageReader(partner_logo_path)
        w = width * 0.50
        images.append((img, w))
        total_width += w

    if os.path.exists(summit_logo_path):
        if images:
            total_width += spacing
        img = ImageReader(summit_logo_path)
        w = width * 0.50
        images.append((img, w))
        total_width += w

    if images:
        start_x = (width - total_width) / 2
        y_pos = height - margin_top - logo_h - s(12)
        for img, w in images:
            c.drawImage(img, start_x, y_pos, width=w, height=logo_h,
                        preserveAspectRatio=True, mask="auto")
            start_x += w + spacing

    # --- Sponsor / Partner Logo Grid ---
    logos_dir = os.path.join(settings.BASE_DIR, "static", "images", "badge_logos")

    if os.path.exists(logos_dir):
        logo_files = sorted([
            os.path.join(logos_dir, f)
            for f in os.listdir(logos_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ])[:20]

        if logo_files:
            num_logos = len(logo_files)
            cols = 5
            rows = math.ceil(num_logos / cols)

            grid_top = height - s(75)
            grid_height = s(95)
            grid_width = width * 0.95

            start_x = (width - grid_width) / 2
            start_y = grid_top - grid_height

            cell_w = grid_width / cols
            cell_h = grid_height / rows

            for idx, logo_path in enumerate(logo_files):
                try:
                    img = ImageReader(logo_path)
                    col = idx % cols
                    row = idx // cols

                    x = start_x + col * cell_w
                    y = start_y + (rows - 1 - row) * cell_h

                    padding = s(1.5)
                    c.drawImage(img,
                                x + padding,
                                y + padding,
                                width=cell_w - padding * 2,
                                height=cell_h - padding * 2,
                                preserveAspectRatio=True,
                                mask="auto")
                except Exception as e:
                    logger.warning(f"Error drawing logo {logo_path}: {str(e)}")
                    pass

    ###############################################################
    # ======================== END PDF ============================
    ###############################################################

    c.save()
    pdf_buffer.seek(0)

    # Cleanup QR buffer to free memory
    if qr_buffer:
        qr_buffer.close()

    return pdf_buffer


def generate_badge_filename(registrant):
    """
    Generate a unique filename for the badge PDF.

    Args:
        registrant: Registrant model instance

    Returns:
        str: Filename for the badge PDF
    """
    full_name = registrant.get_full_name() or f"registrant_{registrant.id}"
    # Clean up name for filesystem
    safe_name = full_name.strip().replace(" ", "_").replace("/", "_")
    # Remove any other problematic characters
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))

    # Include ID to ensure uniqueness
    filename = f"badge_{registrant.id}_{safe_name}.pdf"

    return filename  # ✅ ADD "filename" HERE!

def log_pdf_size(file_path, registrant_id):
    """Log PDF file size for monitoring"""
    try:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > 2.0:
            logger.warning(f"⚠️  PDF over 2MB: ID={registrant_id}, Size={size_mb:.2f}MB")
        else:
            logger.info(f"✅ PDF OK: ID={registrant_id}, Size={size_mb:.2f}MB")
        return size_mb
    except Exception as e:
        logger.error(f"Error checking size: {e}")
        return None


def process_single_badge(registrant):
    try:
        category_obj = Category.objects.only("name").get(id=registrant.category)
        category_name = category_obj.name
        category_folder = get_category_folder_path(category_name)

        # Generate badge PDF
        pdf_buffer = build_exhibitor_badge_pdf(registrant)

        filename = generate_badge_filename(registrant)
        file_path = os.path.join(category_folder, filename)

        # Save PDF to file
        with open(file_path, 'wb') as f:
            f.write(pdf_buffer.read())

        # Log file size
        log_pdf_size(file_path, registrant.id)  # <-- ADD THIS LINE

        logger.info(f"✅ Badge generated: {filename} → {category_name}/")
        return True, None, file_path

    except Category.DoesNotExist:
        error_msg = f"Category not found for registrant {registrant.id}"
        logger.error(error_msg)
        return False, error_msg, None

    except Exception as e:
        error_msg = f"Error generating badge for registrant {registrant.id}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, None


def process_batch(batch):
    """
    Process a batch of registrants.

    Args:
        batch: QuerySet or list of Registrant instances

    Returns:
        dict: Statistics about the batch processing
    """
    stats = {
        'total': len(batch),
        'success': 0,
        'failed': 0,
        'errors': [],
        'files_created': []
    }

    for registrant in batch:
        success, error, file_path = process_single_badge(registrant)

        if success:
            # Update is_printed flag
            try:
                with transaction.atomic():
                    registrant.is_printed = 1
                    registrant.save(update_fields=['is_printed'])
                stats['success'] += 1
                stats['files_created'].append(file_path)
            except Exception as e:
                logger.error(f"Failed to update is_printed for {registrant.id}: {str(e)}")
                stats['failed'] += 1
                stats['errors'].append({
                    'registrant_id': registrant.id,
                    'error': f"Database update failed: {str(e)}"
                })
        else:
            stats['failed'] += 1
            stats['errors'].append({
                'registrant_id': registrant.id,
                'error': error
            })

    return stats


def process_all_badges(batch_size=10, max_batches=None, enable_gc=True):
    """
    Process all unprinted registrant badges in batches.
    OPTIMIZED FOR LIMITED RESOURCES - handles large datasets efficiently.

    Args:
        batch_size (int): Number of registrants to process per batch (default: 10)
        max_batches (int, optional): Maximum number of batches to process (for testing)
        enable_gc (bool): Force garbage collection after each batch (default: True)

    Returns:
        dict: Overall statistics
    """
    import gc

    logger.info("=" * 70)
    logger.info("🎫 BATCH BADGE GENERATION STARTED")
    logger.info("=" * 70)

    # Query registrants that haven't been printed
    # Use only() to fetch minimal fields for counting
    # ✅ Process only registrants with specific IDs
    ids_to_process = [2187]  # <-- put your desired IDs here
    unprinted_query = Registrant.objects.filter(id__in=ids_to_process)

    total_count = unprinted_query.count()
    logger.info(f"📊 Found {total_count} registrants to process")

    if total_count == 0:
        logger.info("✅ No registrants to process. All badges are up to date!")
        return {'total': 0, 'success': 0, 'failed': 0}

    overall_stats = {
        'total': total_count,
        'success': 0,
        'failed': 0,
        'batches_processed': 0,
        'error_count': 0,  # Just count, don't store all errors
        'all_files': []
    }

    # Process in batches using iterator (memory efficient)
    batch_num = 0
    total_batches = (total_count + batch_size - 1) // batch_size

    # Use iterator() to avoid caching all objects in memory
    offset = 0
    while offset < total_count:
        if max_batches and batch_num >= max_batches:
            logger.info(f"⚠️  Reached maximum batch limit ({max_batches}). Stopping.")
            break

        batch_num += 1

        # Fetch only the current batch with select_related for category
        batch = list(
            unprinted_query[offset:offset + batch_size]
        )

        if not batch:
            break

        logger.info(f"\n{'─' * 70}")
        logger.info(f"📦 Processing Batch {batch_num}/{total_batches}")
        logger.info(f"📝 Registrants {offset + 1} to {offset + len(batch)}")
        logger.info(f"{'─' * 70}")

        batch_stats = process_batch(batch)

        # Update overall statistics
        overall_stats['success'] += batch_stats['success']
        overall_stats['failed'] += batch_stats['failed']
        overall_stats['batches_processed'] += 1
        overall_stats['error_count'] += len(batch_stats['errors'])
        overall_stats['all_files'].extend(batch_stats['files_created'])

        # Log batch results
        logger.info(f"📊 Batch {batch_num} Complete:")
        logger.info(f"   ✅ Success: {batch_stats['success']}/{batch_stats['total']}")
        logger.info(f"   ❌ Failed: {batch_stats['failed']}/{batch_stats['total']}")

        # Log errors for this batch only (don't accumulate)
        if batch_stats['errors']:
            logger.info(f"   ⚠️  Errors in this batch:")
            for error in batch_stats['errors'][:3]:  # Show max 3 errors per batch
                logger.info(f"      - Registrant {error['registrant_id']}: {error['error']}")

        # Clear batch from memory
        del batch
        del batch_stats

        # Force garbage collection to free memory
        if enable_gc:
            gc.collect()

        offset += batch_size

    # Final summary
    logger.info("\n" + "=" * 70)
    logger.info("🎉 FINAL SUMMARY")
    logger.info("=" * 70)
    logger.info(f"📊 Total Registrants: {overall_stats['total']}")
    logger.info(f"📦 Batches Processed: {overall_stats['batches_processed']}")
    logger.info(f"✅ Successfully Generated: {overall_stats['success']}")
    logger.info(f"❌ Failed: {overall_stats['failed']}")

    if overall_stats['total'] > 0:
        success_rate = (overall_stats['success'] / overall_stats['total'] * 100)
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")

    logger.info(f"📁 Total Files Created: {len(overall_stats['all_files'])}")

    if overall_stats['error_count'] > 0:
        logger.info(f"\n⚠️  Total Errors: {overall_stats['error_count']}")
        logger.info(f"   (Check logs above for details)")

    logger.info("=" * 70)
    logger.info("✅ Badge generation complete!")
    logger.info("=" * 70)

    # Final cleanup
    if enable_gc:
        import gc
        gc.collect()

    return overall_stats


def process_specific_categories(category_names, batch_size=10):
    """
    Process badges for specific categories only.

    Args:
        category_names (list): List of category names to process
        batch_size (int): Number of registrants per batch

    Returns:
        dict: Overall statistics
    """
    logger.info(f"🎯 Processing specific categories: {', '.join(category_names)}")

    categories = Category.objects.filter(name__in=category_names)
    category_ids = list(categories.values_list('id', flat=True))

    if not category_ids:
        logger.error("❌ No matching categories found!")
        return {'total': 0, 'success': 0, 'failed': 0}

    # Filter by categories and unprinted status
    unprinted = (
        Registrant.objects.filter(category__in=category_ids, is_printed__isnull=True) |
        Registrant.objects.filter(category__in=category_ids).exclude(is_printed=1)
    )

    total_count = unprinted.count()
    logger.info(f"📊 Found {total_count} registrants in selected categories")

    if total_count == 0:
        logger.info("✅ No registrants to process in these categories!")
        return {'total': 0, 'success': 0, 'failed': 0}

    return process_all_badges(batch_size=batch_size)


# Convenience functions for common operations
def process_first_10():
    """
    Process ONLY the first 10 unprinted registrants.
    HIGH QUALITY - No size limits, best quality PDFs.
    Perfect for initial run and testing.
    """
    import gc

    logger.info("=" * 70)
    logger.info("🎫 PROCESSING FIRST 10 REGISTRANTS - HIGH QUALITY MODE")
    logger.info("=" * 70)

    # Query first 10 unprinted registrants
    unprinted_query = (
        Registrant.objects.filter(is_printed__isnull=True) |
        Registrant.objects.exclude(is_printed=1)
    )

    total_available = unprinted_query.count()
    logger.info(f"📊 Total unprinted registrants: {total_available}")

    if total_available == 0:
        logger.info("✅ No registrants to process!")
        return {'total': 0, 'success': 0, 'failed': 0}

    # Get first 10 only
    batch = list(unprinted_query[:10])
    actual_count = len(batch)

    logger.info(f"🎯 Processing: {actual_count} registrants")
    logger.info(f"📄 Quality: MAXIMUM (no compression)")
    logger.info("=" * 70)

    stats = {
        'total': actual_count,
        'success': 0,
        'failed': 0,
        'errors': []
    }

    # Process each registrant
    for idx, registrant in enumerate(batch, 1):
        logger.info(f"\n🔄 Processing {idx}/{actual_count}: ID={registrant.id}")
        logger.info(f"   Name: {registrant.get_full_name()}")

        success, error, file_path = process_single_badge(registrant)

        if success:
            # Update is_printed flag
            try:
                with transaction.atomic():
                    registrant.is_printed = 1
                    registrant.save(update_fields=['is_printed'])
                stats['success'] += 1

                # Get file size
                if file_path and os.path.exists(file_path):
                    file_size = os.path.getsize(file_path) / 1024  # KB
                    logger.info(f"   ✅ SUCCESS - File: {os.path.basename(file_path)}")
                    logger.info(f"   📊 Size: {file_size:.1f} KB")
                else:
                    logger.info(f"   ✅ SUCCESS")

            except Exception as e:
                logger.error(f"   ❌ FAILED: Database update error - {str(e)}")
                stats['failed'] += 1
                stats['errors'].append({
                    'registrant_id': registrant.id,
                    'name': registrant.get_full_name(),
                    'error': f"DB update failed: {str(e)}"
                })
        else:
            logger.error(f"   ❌ FAILED: {error}")
            stats['failed'] += 1
            stats['errors'].append({
                'registrant_id': registrant.id,
                'name': registrant.get_full_name(),
                'error': error
            })

    # Cleanup
    del batch
    gc.collect()

    # Final summary
    logger.info("\n" + "=" * 70)
    logger.info("🎉 FIRST 10 PROCESSING COMPLETE")
    logger.info("=" * 70)
    logger.info(f"✅ Successfully Generated: {stats['success']}/{stats['total']}")
    logger.info(f"❌ Failed: {stats['failed']}/{stats['total']}")

    if stats['success'] > 0:
        success_rate = (stats['success'] / stats['total'] * 100)
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")

    if stats['errors']:
        logger.info(f"\n⚠️  Errors:")
        for error in stats['errors']:
            logger.info(f"   • ID {error['registrant_id']} ({error['name']}): {error['error']}")

    logger.info("=" * 70)

    return stats


def test_single_batch():
    """Test with a single batch of 10 registrants."""
    logger.info("🧪 Running test with single batch...")
    return process_all_badges(batch_size=10, max_batches=1)


def process_all():
    """Process all unprinted badges."""
    return process_all_badges(batch_size=10)


def process_conservative(batch_size=5):
    """
    Conservative processing for very limited resources.
    Smaller batches + aggressive garbage collection.

    Recommended for:
    - Systems with < 2GB RAM
    - Shared hosting environments
    - When experiencing memory issues
    """
    import time

    logger.info("🐌 Running in CONSERVATIVE mode (slower but safer)")
    logger.info(f"   Batch size: {batch_size}")
    logger.info(f"   Garbage collection: Aggressive")
    logger.info(f"   Pause between batches: 2 seconds")

    # Query total count
    unprinted_query = (
        Registrant.objects.filter(is_printed__isnull=True) |
        Registrant.objects.exclude(is_printed=1)
    )
    total_count = unprinted_query.count()

    if total_count == 0:
        logger.info("✅ No registrants to process.")
        return {'total': 0, 'success': 0, 'failed': 0}

    logger.info(f"📊 Total to process: {total_count}")
    estimated_time = (total_count / batch_size) * 10  # rough estimate
    logger.info(f"⏱️  Estimated time: ~{estimated_time/60:.1f} minutes")

    stats = {
        'total': total_count,
        'success': 0,
        'failed': 0,
        'batches': 0
    }

    offset = 0
    batch_num = 0

    while offset < total_count:
        batch_num += 1

        # Fetch minimal batch
        batch = list(
            unprinted_query[offset:offset + batch_size]
        )

        if not batch:
            break

        logger.info(f"\n📦 Batch {batch_num} ({offset + 1}-{offset + len(batch)} of {total_count})")

        # Process batch
        for registrant in batch:
            success, error, file_path = process_single_badge(registrant)

            if success:
                try:
                    with transaction.atomic():
                        registrant.is_printed = 1
                        registrant.save(update_fields=['is_printed'])
                    stats['success'] += 1
                    logger.info(f"   ✅ {registrant.id}")
                except Exception as e:
                    stats['failed'] += 1
                    logger.error(f"   ❌ {registrant.id}: DB update failed")
            else:
                stats['failed'] += 1
                logger.error(f"   ❌ {registrant.id}: {error}")

        stats['batches'] += 1

        # Aggressive cleanup
        del batch
        import gc
        gc.collect()

        # Pause to let system breathe
        time.sleep(2)

        offset += batch_size

    logger.info(f"\n✅ Conservative processing complete!")
    logger.info(f"   Success: {stats['success']}/{stats['total']}")
    logger.info(f"   Failed: {stats['failed']}/{stats['total']}")

    return stats


def estimate_resources():
    """
    Estimate memory usage for badge generation.
    Helps determine optimal batch size.
    """
    import sys

    logger.info("=" * 70)
    logger.info("📊 RESOURCE ESTIMATION")
    logger.info("=" * 70)

    # Count registrants
    unprinted = (
        Registrant.objects.filter(is_printed__isnull=True) |
        Registrant.objects.exclude(is_printed=1)
    )
    total = unprinted.count()

    # Rough estimates
    mb_per_badge = 2  # Average: QR code + images + PDF
    mb_per_registrant = 0.1  # Django model in memory

    logger.info(f"📝 Registrants to process: {total}")
    logger.info(f"\n💾 Estimated Memory Usage:")
    logger.info(f"   Batch of 5:  {(5 * mb_per_badge + 5 * mb_per_registrant):.1f} MB")
    logger.info(f"   Batch of 10: {(10 * mb_per_badge + 10 * mb_per_registrant):.1f} MB")
    logger.info(f"   Batch of 20: {(20 * mb_per_badge + 20 * mb_per_registrant):.1f} MB")

    logger.info(f"\n⏱️  Estimated Time (rough):")
    logger.info(f"   Batch of 5:  ~{(total / 5 * 8 / 60):.1f} minutes")
    logger.info(f"   Batch of 10: ~{(total / 10 * 8 / 60):.1f} minutes")
    logger.info(f"   Batch of 20: ~{(total / 20 * 8 / 60):.1f} minutes")

    logger.info(f"\n💡 RECOMMENDATIONS:")
    if total > 1000:
        logger.info("   ⚠️  Large dataset detected!")
        logger.info("   • Start with test_single_batch() first")
        logger.info("   • Use process_conservative(batch_size=5) for safety")
        logger.info("   • Consider running overnight")
        logger.info("   • Monitor system resources")
    else:
        logger.info("   • Standard batch_size=10 should work fine")
        logger.info("   • Run process_all_badges()")

    logger.info("=" * 70)


if __name__ == "__main__":
    # When run directly, process all badges
    process_all_badges(batch_size=10)