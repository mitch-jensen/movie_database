from typing import List, Self
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import datetime


def validate_year(value):
    min_year = 1900
    max_year = 9999
    if value.year < min_year or value.year > max_year:
        raise ValidationError(
            f"Year must be between {min_year} and {max_year}")


def movie_year_factory(year):
    """
    Returns a datetime object with the specified year, week 1, and day 1. Used for the year column in the movie class (we generally don't care about day and month of release).
    """
    return datetime(year=year, month=1, day=1)


class MultiMovieSet(models.Model):
    title = models.TextField()
    movies = models.ManyToManyField('Movie', related_name='movies')

    def __str__(self):
        movies = self.movies.all()
        movie_titles = [str(movie) for movie in movies]
        return f'''{self.title} <{', '.join(movie_titles)}>'''

    class Meta:
        db_table = 'multi_movie_set'
        ordering = ['title']


class Movie(models.Model):
    class Medium(models.TextChoices):
        DVD = 'D', _('DVD')
        BLURAY = 'B', _('Blu-ray')
        BLURAY4K = '4', _('4K Blu-ray')

    class Distributor(models.TextChoices):
        ONE_OH_ONE_ONE = "101", _("101 Films")
        TWENTIETH_CENTURY_FOX = "20t", _("20th Century Fox")
        EIGHTY_EIGHT_FILMS = "88F", _("88 Films")
        ARROW = "Arr", _("Arrow")
        BFI_VIDEO = "BFI", _("BFI Video")
        BEYOND_HOME_ENTERTAINMENT = "Bey", _("Beyond Home Entertainment")
        BLUE_UNDERGROUND = "Blu", _("Blue Underground")
        CODE_RED = "Cod", _("Code Red")
        CRITERION = "Cri", _("Criterion")
        DARK_FORCE_ENTERTAINMENT = "Dar", _("Dark Force Entertainment")
        DUKE_MARKETING = "Duk", _("Duke Marketing")
        ENTERTAINMENT_ONE = "Ent", _("Entertainment One")
        EUREKA_ENTERTAINMENT = "Eur", _("Eureka Entertainment")
        FILM_CHEST = "Fil", _("Film Chest")
        FOX_MGM = "Fox", _("Fox/MGM")
        GLASS_DOLL_FILMS = "Gla", _("Glass Doll Films")
        GRINDHOUSE_RELEASING = "Gri", _("Grindhouse Releasing")
        GRYPHON_ENTERTAINMENT = "Gry", _("Gryphon Entertainment")
        ICON_FILM_DISTRIBUTION = "Ico", _("Icon Film Distribution")
        IMPRINT = "Imp", _("Imprint")
        KINO_LORBER = "Kin", _("Kino Lorber")
        MPI_MEDIA_GROUP = "MPI", _("MPI Media Group")
        MADMAN_ENTERTAINMENT = "Mad", _("Madman Entertainment")
        METRO_GOLDWYN_MAYER = "Met", _("Metro-Goldwyn-Mayer")
        MILL_CREEK_ENTERTAINMENT = "Mil", _("Mill Creek Entertainment")
        MONDO_MACABRO = "Mod", _("Mondo Macabro")
        MONSTER_PICTURES = "Mon", _("Monster Pictures")
        NETWORK = "Net", _("Network")
        OLIVE_FILMS = "Oli", _("Olive Films")
        PARAMOUNT_PICTURES = "Par", _("Paramount Pictures")
        POWERHOUSE_FILMS = "Pow", _("Powerhouse Films")
        RLJ_ENTERTAINMENT = "RLJ", _("RLJ Entertainment")
        RAROVIDEO_US = "Rar", _("RaroVideo U.S.")
        REDEMPTION = "Red", _("Redemption")
        REEL = "Ree", _("Reel")
        RETROMEDIA = "Ret", _("Retromedia")
        ROADSHOW_ENTERTAINMENT = "Roa", _("Roadshow Entertainment")
        RONIN_FLIX = "Ron", _("Ronin Flix")
        SRS_CINEMA = "SRS", _("SRS Cinema")
        SATURNS_CORE_AUDIO_VIDEO = "Sat", _("Saturn's Core Audio & Video")
        SCORPION_RELEASING = "Sco", _("Scorpion Releasing")
        SCREENBOUND_PICTURES = "Scr", _("Screenbound Pictures")
        SECOND_SIGHT = "Sec", _("Second Sight")
        SEVERIN_FILMS = "Sev", _("Severin Films")
        SHOCK = "Shc", _("Shock")
        SHOUT_FACTORY = "Sho", _("Shout Factory")
        SHRIEK_SHOW = "Shr", _("Shriek Show")
        SIREN_VISUAL_ENTERTAINMENT = "Sir", _("Siren Visual Entertainment")
        SONY_PICTURES = "Son", _("Sony Pictures")
        STARZ_ANCHOR_BAY = "Sta", _("Starz / Anchor Bay")
        STUDIO_CANAL = "Stu", _("Studio Canal")
        SYNAPSE_FILMS = "Syn", _("Synapse Films")
        TEMPE_DIGITAL = "Tem", _("Tempe Digital")
        TERROR_VISION = "Ter", _("Terror Vision")
        THE_FILM_DETECTIVE = "The", _("The Film Detective")
        TROMA = "Tro", _("Troma")
        UMBRELLA_ENTERTAINMENT = "Umb", _("Umbrella Entertainment")
        UNIVERSAL_STUDIOS = "Uni", _("Universal Studios")
        VCI = "VCI", _("VCI")
        VIA_VISION_ENTERTAINMENT = "Via", _("Via Vision Entertainment")
        VINEGAR_SYNDROME = "Vin", _("Vinegar Syndrome")
        VISUAL_ENTERTAINMENT_GROUP = "Vis", _("Visual Entertainment Group")
        WARNER_BROS = "War", _("Warner Bros.")
        WICKED_VISION_MEDIA = "Wic", _("Wicked-Vision Media")

    class Prefix(models.TextChoices):
        THE = "The", _("The")
        A = "A", _("A")
        AN = "An", _("An")

    title = models.TextField()
    year = models.DateField(validators=[validate_year])
    title_prefix = models.TextField(default='')
    medium = models.CharField(
        max_length=1, choices=Medium.choices, default=Medium.BLURAY)
    distributor = models.CharField(max_length=3, choices=Distributor.choices)
    fits_on_shelf = models.BooleanField(default=True)
    upc = models.IntegerField(null=True)
    ean = models.IntegerField(null=True)
    prefix = models.CharField(max_length=3, choices=Prefix.choices, null=True)

    def save(self, *args, **kwargs):
        if not self.prefix and self.title.lower().startswith(('the', 'a', 'an')):
            # Split 'the', 'a' and 'an' from the start of the title for ordering
            self.process_title()

        super().save(*args, **kwargs)

    def process_title(self):
        # Remove 'the', 'a', or 'an' from the start of the title
        prefix = ''
        title_words = self.title.split()
        if len(title_words) > 0 and title_words[0].lower() in ['the', 'a', 'an']:
            prefix = title_words.pop(0)

        # Update 'prefix' and 'title' fields
        self.prefix = prefix
        self.title = ' '.join(title_words)

    @classmethod
    def collection(cls) -> List[str]:
        return sorted(cls.objects.all(), key=lambda movie: movie.title_prefix + str(movie).strip().lower().removeprefix('the').removeprefix('a').removeprefix('an'))

    def __str__(self):
        prefix = ''
        if self.prefix:
            prefix = self.prefix + ' '
        return f'{prefix}{self.title} ({self.year.year})'

    class Meta:
        db_table = 'movie'
        ordering = ['title']
