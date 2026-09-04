import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from clubs.models import Club, ClubMember
from posts.models import Post

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial superuser and movie clubs if database is empty'

    def handle(self, *args, **options):
        # 1. Create Superuser if no superuser exists
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'AdminPass123!')
        
        if not User.objects.filter(is_superuser=True).exists():
            admin_user = User.objects.create_superuser(
                email=admin_email,
                password=admin_password,
                name='Platform Admin',
                bio='System Administrator for Movie & Series Club App'
            )
            self.stdout.write(self.style.SUCCESS(f'Created Superuser: {admin_email}'))
        else:
            admin_user = User.objects.filter(is_superuser=True).first()

        # 2. Seed Default Genre Clubs if no clubs exist
        if not Club.objects.exists():
            seed_clubs = [
                {'name': 'Sci-Fi Cinephiles', 'genre': 'Science Fiction', 'description': 'Exploring futuristic worlds, cyberpunk classics, and space operas.'},
                {'name': 'Horror Vault', 'genre': 'Horror', 'description': 'For fans of psychological thrillers, slasher classics, and supernatural horror.'},
                {'name': 'Indie Film Society', 'genre': 'Drama', 'description': 'Appreciating independent cinema, festival darlings, and auteur directors.'},
                {'name': 'Animation & Anime Guild', 'genre': 'Animation', 'description': 'Celebrating animated masterpieces from Studio Ghibli, Pixar, and beyond.'},
                {'name': 'Action & Adventure Club', 'genre': 'Action', 'description': 'High-octane blockbusters, martial arts cinema, and epic adventures.'},
            ]
            for club_data in seed_clubs:
                club = Club.objects.create(
                    name=club_data['name'],
                    genre=club_data['genre'],
                    description=club_data['description'],
                    created_by=admin_user
                )
                ClubMember.objects.create(club=club, user=admin_user)
                self.stdout.write(self.style.SUCCESS(f'Created Club: {club.name} ({club.genre})'))
        
        # 3. Seed Sample Movie Post if no posts exist
        if not Post.objects.exists():
            Post.objects.create(
                user=admin_user,
                movie_id=550,
                movie_title='Fight Club',
                body='An absolute masterpiece of psychological drama and storytelling.',
                stars=5
            )
            self.stdout.write(self.style.SUCCESS('Created initial sample post'))
