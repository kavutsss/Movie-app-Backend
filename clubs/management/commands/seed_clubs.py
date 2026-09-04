"""
Usage: python manage.py seed_clubs
Safe to run multiple times — skips clubs that already exist.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from clubs.models import Club, ClubMember

User = get_user_model()

CLUBS = [
    {"name": "Afrocinema", "description": "Celebrating African films, directors and storytelling from across the continent.", "genre": "World"},
    {"name": "Anime & Manga Adaptations", "description": "Comparing anime source material to live action adaptations — what works and what does not.", "genre": "Sci-Fi"},
    {"name": "K-Drama Addicts", "description": "Korean dramas, romance, thrillers and everything in between. No spoilers without warning.", "genre": "Drama"},
    {"name": "Bollywood Masala", "description": "Indian cinema from golden classics to modern blockbusters. Dance, drama and everything masala.", "genre": "World"},
    {"name": "Documentary Hunters", "description": "True crime, nature, history and social documentaries. If it is real, we watch it.", "genre": "Documentary"},
    {"name": "Feel Good Films", "description": "Movies that leave you smiling no matter what. Bring your recommendations and good vibes only.", "genre": "Comedy"},
    {"name": "Midnight Cinema", "description": "Late night watches, cult classics and hidden gems best enjoyed after dark.", "genre": "Noir"},
    {"name": "Cry Club", "description": "Films that hit different emotionally. Tissues required. No judgment here.", "genre": "Drama"},
    {"name": "Comfort Rewatch", "description": "Movies you have seen 10 or more times and still love. Share your ultimate comfort films.", "genre": "Drama"},
    {"name": "First Time Watchers", "description": "Reacting to classics for the first time. Fresh eyes, honest takes.", "genre": "Art House"},
    {"name": "One Film A Week", "description": "Commit to watching and reviewing one film every week. Consistency builds taste.", "genre": "Drama"},
    {"name": "Underrated & Overlooked", "description": "Films that deserved way more attention. Hidden gems and forgotten masterpieces only.", "genre": "Art House"},
    {"name": "Directors Spotlight", "description": "Deep diving one director at a time — Kubrick, Nolan, Villeneuve, Kurosawa and beyond.", "genre": "Art House"},
    {"name": "Sequel vs Original", "description": "Debating whether sequels lived up to the original. Honest comparisons, no nostalgia bias.", "genre": "Thriller"},
    {"name": "Binge or Skip", "description": "Honest reviews on whether a series is worth your time. Save people from bad TV.", "genre": "Drama"},
    {"name": "Cancelled Too Soon", "description": "Mourning shows that ended before their time. A support group for the heartbroken.", "genre": "Drama"},
    {"name": "Finale Reactions", "description": "Discussing series finales good and bad. Did it stick the landing or ruin everything?", "genre": "Thriller"},
]


class Command(BaseCommand):
    help = "Seed the database with default film clubs"

    def handle(self, *args, **kwargs):
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.stderr.write("No superuser found. Run: python manage.py createsuperuser")
            return

        created_count = 0
        skipped_count = 0

        for data in CLUBS:
            club, created = Club.objects.get_or_create(
                name=data["name"],
                defaults={"description": data["description"], "genre": data["genre"], "created_by": admin},
            )
            if created:
                ClubMember.objects.get_or_create(club=club, user=admin)
                self.stdout.write(f"  Created: {club.name}")
                created_count += 1
            else:
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone — {created_count} clubs created, {skipped_count} already existed."
        ))
