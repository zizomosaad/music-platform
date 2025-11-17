import os
import django

# adjust if your settings module path is different
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from artists.models import Artist
from datetime import datetime, timedelta
from decimal import Decimal
from albums.models import Albums
from django.utils import timezone

artists = [
    {"stage_name": "Adele", "social_link": "https://example.com/adele"},
    {"stage_name": "Drake", "social_link": ""},
    {"stage_name": "The Weeknd", "social_link": "https://example.com/weeknd"},
]

for a in artists:
    obj, created = Artist.objects.get_or_create(
        stage_name=a["stage_name"],
        defaults={"social_link": a["social_link"]},
    )
    print("created" if created else "exists:", obj)

print("\nALL ARTISTS:")
for a in Artist.objects.all():
    print(a.pk, a.stage_name, a.social_link)
print('\n')

# 3) All artists sorted by name
qs = Artist.objects.order_by('stage_name')
print("Artists sorted by name:")
for a in qs:
    print(a.pk, a.stage_name, a.social_link)
print('\n')

# 4) All artists whose name starts with "a" (case-insensitive), sorted by name
print('Artists whose name starts with "a":')
qs_a = Artist.objects.filter(stage_name__istartswith='a').order_by('stage_name')
for a in qs_a:
    print(a.pk, a.stage_name, a.social_link)
print('\n')

# 5) Create two albums in two different ways and assign them to an artist
print("Creating albums:")
deleted = Albums.objects.filter(pk__in=[1,2]).delete()  # clean up previous runs
# --- Way 1: use the Album manager ---
adele = Artist.objects.get(stage_name="Adele")
Albums.objects.get_or_create(
    artist=adele,
    name="25",
    release_date=datetime(2015, 11, 20 , 4 , 15),
    cost=Decimal("9.99"),
)

# --- Way 2: use the related-object manager on the Artist instance ---
drake = Artist.objects.get(stage_name="Drake")
# if you did not set related_name on the FK, use album_set; if you set related_name='albums' use drake.albums.create(...)
drake.albums.get_or_create(
    name="Scorpion",
    release_date=datetime(2018, 6, 29 , 15 , 30 ),
    cost=Decimal("11.99"),
)

print('\n')
tz = timezone.get_current_timezone()

def aware_dt(y, m, d, H=0, M=0):
    return timezone.make_aware(datetime(y, m, d, H, M), tz)

album_specs = [
    # past releases
    {"artist_name": "Adele", "name": "19", "release_date": aware_dt(2008, 1, 28), "cost": Decimal("7.99")},
    {"artist_name": "Adele", "name": "25", "release_date": aware_dt(2015, 11, 20, 4, 15), "cost": Decimal("9.99")},
    {"artist_name": "Drake", "name": "Thank Me Later", "release_date": aware_dt(2010, 6, 15), "cost": Decimal("8.99")},
    # recent past
    {"artist_name": "Drake", "name": "Scorpion", "release_date": aware_dt(2018, 6, 29, 15, 30), "cost": Decimal("11.99")},
    # today
    {"artist_name": "The Weeknd", "name": "Today's Single", "release_date": timezone.now(), "cost": Decimal("1.29")},
    # near future
    {"artist_name": "The Weeknd", "name": "Future EP", "release_date": timezone.now() + timedelta(days=30), "cost": Decimal("4.99")},
    # far future
    {"artist_name": "Adele", "name": "Next Album", "release_date": timezone.now() + timedelta(days=365), "cost": Decimal("12.99")},
]

for spec in album_specs:
    artist, _ = Artist.objects.get_or_create(stage_name=spec["artist_name"])
    Albums.objects.get_or_create(
        artist=artist,
        name=spec["name"],
        defaults={
            "release_date": spec["release_date"],
            "cost": spec["cost"],
        },
    )

# print all albums to verify
for a in Albums.objects.select_related("artist").order_by("release_date"):
    print(a.pk, a.name, a.artist.stage_name, a.release_date, a.cost)


# 6) get the latest released album

print('\nLatest released album:')

album = Albums.objects.latest('release_date')
print(album.pk , album.name)

# 7) get all albums released before today
print('\nAlbums released before today:')

today = timezone.now()

qs = Albums.objects.filter(release_date__lt=today)
for a in qs:
    print(a.pk, a.name, a.artist.stage_name, a.release_date, a.cost)

# 8) count all albums

print('\nTotal number of albums:')

albums_count = Albums.objects.count()
print(albums_count)

# 9) list down all albums per artist

print('\nAlbums per artist:')

artists = Artist.objects.prefetch_related('albums').all().order_by('stage_name')
# for artist in artists :
#     print(f'Albums by {artist.stage_name}:')
#     for album in artist.albums.all():
#         print(f'    {album.pk} - {album.name} - Released on: {album.release_date} - Cost: {album.cost}')
for artist in artists:
    albums = Albums.objects.filter(artist=artist).order_by('release_date')
    print(f'Albums by {artist.stage_name}:')
    for album in albums:
        print(f'    {album.pk} - {album.name} - Released on: {album.release_date} - Cost: {album.cost}')
        

