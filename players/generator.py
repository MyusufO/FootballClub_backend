import random

FIRST_NAMES = (
    'Luca', 'Mateo', 'Diego', 'Andrés', 'Marco', 'Kylian', 'Jonas', 'Emil',
    'Tobias', 'Rafael', 'Thiago', 'Bruno', 'João', 'Pedro', 'Nikola', 'Luka',
    'Milan', 'Antoine', 'Hugo', 'Théo', 'Karim', 'Youssef', 'Amine', 'Sadio',
    'Kwame', 'Kofi', 'Jamal', 'Malik', 'Leon', 'Finn', 'Oscar', 'Hiro',
    'Takumi', 'Min-jun', 'Kenji', 'Ivan', 'Dmitri', 'Sergei', 'Adam', 'Noah',
)

LAST_NAMES = (
    'Ferreira', 'Silva', 'Costa', 'Morales', 'Ramírez', 'Torres', 'Navarro',
    'Bianchi', 'Romano', 'Rossi', 'Dubois', 'Laurent', 'Moreau', 'Schmidt',
    'Weber', 'Hoffmann', 'Kovač', 'Petrović', 'Nowak', 'Johansson', 'Lindqvist',
    'Andersen', 'Bakker', 'de Vries', 'Okafor', 'Mensah', 'Traoré', 'Diallo',
    'Haddad', 'Karim', 'Yamamoto', 'Tanaka', 'Park', 'Kim', 'Petrov', 'Volkov',
    'Novak', 'Horvat', 'Fischer', 'Vidal',
)

COUNTRIES = (
    'Argentina', 'Belgium', 'Brazil', 'Cameroon', 'Colombia', 'Croatia',
    'Denmark', 'Egypt', 'England', 'France', 'Germany', 'Ghana', 'Italy',
    'Japan', 'Mexico', 'Morocco', 'Netherlands', 'Nigeria', 'Norway', 'Poland',
    'Portugal', 'Senegal', 'Serbia', 'South Korea', 'Spain', 'Sweden',
    'Switzerland', 'Uruguay',
)

CLUBS = (
    'Real Madrid', 'Barcelona', 'Manchester City', 'Liverpool', 'Bayern Munich',
    'Paris Saint-Germain', 'Inter Milan', 'AC Milan', 'Juventus', 'Ajax',
    'Benfica', 'Porto', 'Borussia Dortmund', 'Atlético Madrid', 'Arsenal',
    'Chelsea', 'Napoli', 'Sevilla', 'Sporting CP', 'Lyon',
)

POSITIONS = ('GK', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'ST')

AGE_DEFAULT = (16, 36)
RATING_DEFAULT = (60, 92)
POTENTIAL_HEADROOM = (0, 6)

DOMAINS = {
    'age': (16, 60),
    'rating': (0, 100),
    'potential': (0, 100),
}


def generate_player(overrides, rng=random):
    ranges = overrides['ranges']

    age = _pick(ranges.get('age'), AGE_DEFAULT, 'age', rng, integer=True)
    rating = _pick(ranges.get('rating'), RATING_DEFAULT, 'rating', rng, integer=False)

    potential_bounds = ranges.get('potential')
    if potential_bounds:
        potential = _pick(potential_bounds, RATING_DEFAULT, 'potential', rng, integer=False)
    else:
        potential = rating + rng.randint(*POTENTIAL_HEADROOM)
    potential = round(min(max(potential, rating), DOMAINS['potential'][1]), 1)

    return {
        'name': overrides.get('name') or f'{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}',
        'age': age,
        'position': overrides.get('position') or rng.choice(POSITIONS),
        'country': overrides.get('country') or rng.choice(COUNTRIES),
        'club': overrides.get('club') or rng.choice(CLUBS),
        'rating': rating,
        'potential': potential,
    }


def _pick(bounds, default_bounds, field, rng, integer):
    low, high = _resolve(bounds, default_bounds, DOMAINS[field])
    if integer:
        return rng.randint(low, high)
    return round(rng.uniform(low, high), 1)


def _resolve(bounds, default_bounds, domain):
    if not bounds:
        return default_bounds

    low = bounds.get('min', default_bounds[0])
    high = bounds.get('max', default_bounds[1])
    if low <= high:
        return low, high

    # a lone bound outside the typical range widens to the field's legal domain
    if 'max' not in bounds:
        return low, domain[1]
    return domain[0], high
