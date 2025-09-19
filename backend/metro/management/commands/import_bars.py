import csv
import math
from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand, CommandError

from metro.models import (
    Bar, BarCategory, BarBusinessHours, Station
)


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in meters between two WGS84 points."""
    R = 6371000.0  # meters
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlambda = math.radians(float(lon2) - float(lon1))
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def parse_decimal(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip()
    if s == "" or s.lower() in {"none", "null"}:
        return None
    try:
        return float(s)
    except Exception:
        return None


class Command(BaseCommand):
    help = "Import bar data from a CSV file. Auto-links nearby metro stations and categories."

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True, help="Path to CSV file")
        parser.add_argument("--station-radius-m", type=int, default=500, help="Radius in meters to link nearby stations (default: 500)")
        parser.add_argument("--encoding", default="utf-8", help="CSV encoding (default: utf-8)")

    def handle(self, *args, **options):
        csv_path = Path(options["--csv"]).expanduser().resolve()
        radius_m = options["--station-radius-m"]
        encoding = options["--encoding"]

        if not csv_path.exists():
            raise CommandError(f"CSV not found: {csv_path}")

        required_columns = {"name", "address", "latitude", "longitude"}
        optional_columns = {
            "phone", "google_place_id", "rating", "price_level", "website", "image", "categories"
        }
        # Optional business hours columns: day{0-6}_open, day{0-6}_close, day{0-6}_closed

        created, updated, skipped = 0, 0, 0

        with csv_path.open("r", encoding=encoding, newline="") as f:
            reader = csv.DictReader(f)
            headers = {h.strip() for h in reader.fieldnames or []}

            missing = required_columns - headers
            if missing:
                raise CommandError(f"CSV missing columns: {', '.join(sorted(missing))}")

            for row in reader:
                name = (row.get("name") or "").strip()
                address = (row.get("address") or "").strip()
                lat = parse_decimal(row.get("latitude"))
                lon = parse_decimal(row.get("longitude"))
                if not name or lat is None or lon is None:
                    skipped += 1
                    continue

                google_place_id = (row.get("google_place_id") or "").strip() or None

                bar = None
                if google_place_id:
                    bar = Bar.objects.filter(google_place_id=google_place_id).first()
                if bar is None:
                    bar = Bar.objects.filter(name=name, address=address).first()

                defaults = {
                    "address": address,
                    "latitude": lat,
                    "longitude": lon,
                    "phone": (row.get("phone") or None),
                    "rating": parse_decimal(row.get("rating")),
                    "price_level": parse_decimal(row.get("price_level")),
                    "website": (row.get("website") or None),
                    "image": (row.get("image") or None),
                }

                if bar is None:
                    bar = Bar(
                        name=name,
                        google_place_id=google_place_id or f"BAR-{name}-{address}"[:100],
                        **defaults,
                    )
                    bar.save()
                    created += 1
                else:
                    # update fields
                    bar.name = name
                    bar.google_place_id = google_place_id or bar.google_place_id
                    for k, v in defaults.items():
                        setattr(bar, k, v)
                    bar.save()
                    updated += 1

                # categories
                categories_str = (row.get("categories") or "").strip()
                if categories_str:
                    category_names = [c.strip() for c in categories_str.split(",") if c.strip()]
                    if category_names:
                        bar.categories.clear()
                        for cname in category_names:
                            cat, _ = BarCategory.objects.get_or_create(name=cname)
                            bar.categories.add(cat)

                # link nearby stations within radius
                station_ids = []
                for station in Station.objects.all():
                    dist = haversine_distance_meters(lat, lon, float(station.latitude), float(station.longitude))
                    if dist <= radius_m:
                        station_ids.append(station.id)
                if station_ids:
                    bar.nearby_stations.set(Station.objects.filter(id__in=station_ids))

                # business hours (optional)
                # expect columns day0_open, day0_close, day0_closed ... day6_*
                hours_any = False
                for day in range(7):
                    open_col = f"day{day}_open"
                    close_col = f"day{day}_close"
                    closed_col = f"day{day}_closed"
                    if open_col in headers or close_col in headers or closed_col in headers:
                        hours_any = True
                        break

                if hours_any:
                    # wipe and recreate
                    bar.business_hours.all().delete()
                    for day in range(7):
                        open_val = (row.get(f"day{day}_open") or "").strip()
                        close_val = (row.get(f"day{day}_close") or "").strip()
                        closed_val = (row.get(f"day{day}_closed") or "").strip().lower()
                        is_closed = closed_val in {"1", "true", "yes", "y"}
                        if is_closed or (not open_val and not close_val):
                            BarBusinessHours.objects.create(
                                bar=bar, day_of_week=day, open_time="00:00", close_time="00:00", is_closed=True
                            )
                        else:
                            # expect HH:MM
                            if len(open_val) == 4 and open_val.isdigit():
                                open_val = f"{open_val[:2]}:{open_val[2:]}"
                            if len(close_val) == 4 and close_val.isdigit():
                                close_val = f"{close_val[:2]}:{close_val[2:]}"
                            BarBusinessHours.objects.create(
                                bar=bar, day_of_week=day, open_time=open_val, close_time=close_val, is_closed=False
                            )

        self.stdout.write(self.style.SUCCESS(
            f"Import completed. created={created}, updated={updated}, skipped={skipped}"
        ))


