from django.db.models import Q

from players.exceptions import PlayerNotFound
from players.generator import generate_player
from players.models import Player
from players.serializers import (
    PlayerQuerySerializer,
    PlayerSerializer,
    RandomPlayerSerializer,
)

SEARCH_FIELDS = ('name', 'club', 'country', 'position')

SUBSTRING_FIELDS = frozenset({'name', 'club'})


def list_players(params):
    criteria = PlayerQuerySerializer(params).validate()

    queryset = _build_queryset(criteria).order_by(*criteria['order_by'])
    total = queryset.count()

    if criteria['offset']:
        queryset = queryset[criteria['offset']:]
    if criteria['limit'] is not None:
        queryset = queryset[:criteria['limit']]
    return queryset, total


def _build_queryset(criteria):
    query = Q()

    for field, values in criteria['filters'].items():
        lookup = f'{field}__icontains' if field in SUBSTRING_FIELDS else f'{field}__iexact'
        field_query = Q()
        for value in values:
            field_query |= Q(**{lookup: value})
        query &= field_query

    search = criteria['search']
    if search:
        search_query = Q()
        for field in SEARCH_FIELDS:
            search_query |= Q(**{f'{field}__icontains': search})
        query &= search_query

    for field, bounds in criteria['ranges'].items():
        if 'min' in bounds:
            query &= Q(**{f'{field}__gte': bounds['min']})
        if 'max' in bounds:
            query &= Q(**{f'{field}__lte': bounds['max']})

    if not query:
        return Player.objects.all()
    return Player.objects.filter(query)


def preview_random_player(params):
    overrides = RandomPlayerSerializer(params).validate()
    return generate_player(overrides)


def get_player(player_id):
    try:
        return Player.objects.get(id=player_id)
    except Player.DoesNotExist:
        raise PlayerNotFound(f'No player with id {player_id}.') from None


def create_player(payload):
    data = PlayerSerializer(payload).validate()
    return Player.objects.create(**data)


def update_player(player, payload, partial):
    data = PlayerSerializer(payload, partial=partial).validate()
    for field, value in data.items():
        setattr(player, field, value)
    player.save(update_fields=list(data) or None)
    return player


def delete_player(player):
    player.delete()
