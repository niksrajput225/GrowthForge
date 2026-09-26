import math
from pathlib import Path
from PIL import Image, ImageDraw

def create_growthforge_icon(size=512, maskable=False):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Scale factors
    scale = size / 512.0
    
    # Background
    if maskable:
        # Full bleed for Android adaptive icons
        draw.rectangle([0, 0, size, size], fill=(8, 12, 20, 255))
    else:
        # Rounded rectangle
        corner_radius = int(110 * scale)
        draw.rounded_rectangle([0, 0, size, size], radius=corner_radius, fill=(8, 12, 20, 255))
        draw.rounded_rectangle([int(6*scale), int(6*scale), size - int(6*scale), size - int(6*scale)],
                               radius=int(104*scale), outline=(6, 182, 212, 75), width=int(4*scale))
    
    center = size / 2.0
    
    # Outer geometric ring
    ring_radius = int(170 * scale)
    draw.ellipse([center - ring_radius, center - ring_radius, center + ring_radius, center + ring_radius],
                 outline=(6, 182, 212, 120), width=int(6 * scale))
                 
    # Inner glowing tech ring
    inner_ring = int(140 * scale)
    draw.ellipse([center - inner_ring, center - inner_ring, center + inner_ring, center + inner_ring],
                 outline=(59, 130, 246, 90), width=int(3 * scale))

    # Base Anvil (Hexagonal / Trapezoid geometry)
    anvil_points = [
        (int(140 * scale), int(340 * scale)),
        (int(372 * scale), int(340 * scale)),
        (int(340 * scale), int(395 * scale)),
        (int(172 * scale), int(395 * scale)),
    ]
    draw.polygon(anvil_points, fill=(6, 182, 212, 255))
    
    anvil_top = [
        (int(120 * scale), int(290 * scale)),
        (int(392 * scale), int(290 * scale)),
        (int(360 * scale), int(330 * scale)),
        (int(152 * scale), int(330 * scale)),
    ]
    draw.polygon(anvil_top, fill=(56, 189, 248, 255))
    
    # Ascension Flame (Golden / Ruby Fire Spear)
    flame_pts = [
        (int(256 * scale), int(95 * scale)),   # Tip
        (int(295 * scale), int(170 * scale)),
        (int(315 * scale), int(220 * scale)),
        (int(290 * scale), int(270 * scale)),
        (int(256 * scale), int(285 * scale)),  # Base center
        (int(222 * scale), int(270 * scale)),
        (int(197 * scale), int(220 * scale)),
        (int(217 * scale), int(170 * scale)),
    ]
    draw.polygon(flame_pts, fill=(245, 158, 11, 255))
    
    # Inner Flame Core (Golden yellow)
    core_flame = [
        (int(256 * scale), int(135 * scale)),
        (int(280 * scale), int(195 * scale)),
        (int(268 * scale), int(255 * scale)),
        (int(256 * scale), int(265 * scale)),
        (int(244 * scale), int(255 * scale)),
        (int(232 * scale), int(195 * scale)),
    ]
    draw.polygon(core_flame, fill=(251, 191, 36, 255))
    
    # White Spark Center
    spark_radius = int(14 * scale)
    draw.ellipse([center - spark_radius, int(230 * scale) - spark_radius,
                  center + spark_radius, int(230 * scale) + spark_radius],
                 fill=(255, 255, 255, 240))

    return img

if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent.parent
    icons_dir = base_dir / 'app' / 'static' / 'icons'
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate 512x512
    icon_512 = create_growthforge_icon(512, maskable=False)
    icon_512.save(str(icons_dir / 'icon-512.png'), 'PNG')
    print("Generated icon-512.png")
    
    # Generate 192x192
    icon_192 = create_growthforge_icon(192, maskable=False)
    icon_192.save(str(icons_dir / 'icon-192.png'), 'PNG')
    print("Generated icon-192.png")
    
    # Generate maskable 512x512
    icon_maskable = create_growthforge_icon(512, maskable=True)
    icon_maskable.save(str(icons_dir / 'icon-maskable-512.png'), 'PNG')
    print("Generated icon-maskable-512.png")
    
    # Generate Android launcher icons (ic_launcher.png)
    android_res = base_dir / 'android' / 'app' / 'src' / 'main' / 'res'
    mipmap_sizes = {
        'mipmap-mdpi': 48,
        'mipmap-hdpi': 72,
        'mipmap-xhdpi': 96,
        'mipmap-xxhdpi': 144,
        'mipmap-xxxhdpi': 192
    }
    for folder, px in mipmap_sizes.items():
        target_folder = android_res / folder
        target_folder.mkdir(parents=True, exist_ok=True)
        img = create_growthforge_icon(px, maskable=False)
        img.save(str(target_folder / 'ic_launcher.png'), 'PNG')
        img_round = create_growthforge_icon(px, maskable=True)
        img_round.save(str(target_folder / 'ic_launcher_round.png'), 'PNG')
        print(f"Generated Android {folder} ({px}x{px})")

    # Generate Feature Graphic for Google Play Store (1024x500)
    feat_img = Image.new('RGBA', (1024, 500), (8, 12, 20, 255))
    draw_feat = ImageDraw.Draw(feat_img)
    # Background gradient or accent
    draw_feat.rectangle([0, 0, 1024, 500], fill=(8, 12, 20, 255))
    # Place large logo at center
    logo_sub = create_growthforge_icon(320, maskable=False)
    feat_img.paste(logo_sub, (512 - 160, 250 - 160), logo_sub)
    store_dir = base_dir / 'store_assets'
    store_dir.mkdir(parents=True, exist_ok=True)
    feat_img.save(str(store_dir / 'playstore_feature_graphic_1024x500.png'), 'PNG')
    icon_512.save(str(store_dir / 'playstore_app_icon_512x512.png'), 'PNG')
    print("Generated Play Store assets in store_assets/")
