from players.exceptions import ValidationError
from players.generator import DOMAINS

PLAYER_FIELDS = {
    'name': str,
    'age': int,
    'position': str,
    'country': str,
    'club': str,
    'rating': float,
    'potential': float,
}

MAX_LENGTHS = {'name': 100, 'position': 50, 'country': 50, 'club': 100}

FILTER_FIELDS = ('name', 'club', 'position', 'country')

RANGE_FIELDS = {'age': int, 'rating': float, 'potential': float}

ORDERABLE = frozenset(PLAYER_FIELDS) | {'id'}

DEFAULT_ORDERING = ('id',)

MAX_LIMIT = 200

RANDOM_STRING_PARAMS = ('name', 'club', 'position', 'country')

RANDOM_RANGE_FIELDS = {'age': int, 'rating': float, 'potential': float}


def _parse_number(raw, caster):
    try:
        number = float(raw)
    except ValueError:
        return None, 'Must be a number.'
    if caster is int and not number.is_integer():
        return None, 'Must be a whole number.'
    return caster(number), None


class PlayerSerializer:
    fields = PLAYER_FIELDS
    max_lengths = MAX_LENGTHS

    def __init__(self, payload, partial=False):
        self.payload = payload
        self.partial = partial

    def validate(self):
        errors = {}
        data = {}

        for field, value in self.payload.items():
            if field not in self.fields:
                errors[field] = 'Unknown field.'
                continue
            try:
                data[field] = self._clean_value(field, value)
            except ValueError as exc:
                errors[field] = str(exc)

        if not self.partial:
            for field in self.fields:
                if field not in data and field not in errors:
                    errors[field] = 'This field is required.'

        if errors:
            raise ValidationError(errors)
        return data

    def _clean_value(self, field, value):
        expected = self.fields[field]

        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError('This field is required.')

        if expected is str:
            if not isinstance(value, str):
                raise ValueError('Must be a string.')
            value = value.strip()
            limit = self.max_lengths[field]
            if len(value) > limit:
                raise ValueError(f'Must be at most {limit} characters.')
            return value

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError('Must be a number.')

        if expected is int and not float(value).is_integer():
            raise ValueError('Must be a whole number.')
        return expected(value)

    @staticmethod
    def to_representation(player):
        data = {'id': player.id}
        data.update({field: getattr(player, field) for field in PLAYER_FIELDS})
        return data


class PlayerQuerySerializer:
    def __init__(self, params):
        self.params = params

    def validate(self):
        errors = {}
        criteria = {
            'search': self._parse_search(),
            'filters': self._parse_filters(),
            'ranges': self._parse_ranges(errors),
            'order_by': self._parse_ordering(errors),
            'offset': self._parse_paging('offset', 0, errors),
            'limit': self._parse_paging('limit', None, errors),
        }

        if criteria['limit'] is not None and criteria['limit'] > MAX_LIMIT:
            errors['limit'] = f'Must be at most {MAX_LIMIT}.'

        if errors:
            raise ValidationError(errors)
        return criteria

    def _parse_search(self):
        search = self.params.get('search')
        if search is None:
            return None
        search = search.strip()
        return search or None

    def _parse_filters(self):
        filters = {}
        for field in FILTER_FIELDS:
            raw = self.params.get(field)
            if not raw:
                continue
            values = [value.strip() for value in raw.split(',') if value.strip()]
            if values:
                filters[field] = values
        return filters

    def _parse_ranges(self, errors):
        ranges = {}
        for field, caster in RANGE_FIELDS.items():
            bounds = {}
            for bound in ('min', 'max'):
                param = f'{bound}_{field}'
                raw = self.params.get(param)
                if raw in (None, ''):
                    continue
                number, error = _parse_number(raw, caster)
                if error:
                    errors[param] = error
                    continue
                bounds[bound] = number

            if 'min' in bounds and 'max' in bounds and bounds['min'] > bounds['max']:
                errors[f'min_{field}'] = f'Must not exceed max_{field}.'
            elif bounds:
                ranges[field] = bounds
        return ranges

    def _parse_ordering(self, errors):
        raw = self.params.get('order_by')
        if not raw:
            return DEFAULT_ORDERING

        fields = []
        for token in raw.split(','):
            token = token.strip()
            descending = token.startswith('-')
            name = token[1:] if descending else token
            if name not in ORDERABLE:
                errors['order_by'] = f'Cannot order by {token!r}.'
                continue
            fields.append(f'-{name}' if descending else name)
        return tuple(fields) or DEFAULT_ORDERING

    def _parse_paging(self, param, default, errors):
        raw = self.params.get(param)
        if raw in (None, ''):
            return default
        try:
            value = int(raw)
        except ValueError:
            errors[param] = 'Must be a whole number.'
            return default
        if value < 0:
            errors[param] = 'Must not be negative.'
            return default
        return value


class RandomPlayerSerializer:
    def __init__(self, params):
        self.params = params

    def validate(self):
        errors = {}
        overrides = {'ranges': {}}

        for param in RANDOM_STRING_PARAMS:
            value = self._parse_text(param, errors)
            if value:
                overrides[param] = value

        for field, caster in RANDOM_RANGE_FIELDS.items():
            bounds = {}
            for bound in ('min', 'max'):
                param = f'{bound}_{field}'
                raw = self.params.get(param)
                if raw in (None, ''):
                    continue
                number, error = _parse_number(raw, caster)
                if error is None:
                    number, error = self._check_domain(number, field)
                if error:
                    errors[param] = error
                    continue
                bounds[bound] = number

            if 'min' in bounds and 'max' in bounds and bounds['min'] > bounds['max']:
                errors[f'min_{field}'] = f'Must not exceed max_{field}.'
            elif bounds:
                overrides['ranges'][field] = bounds

        if errors:
            raise ValidationError(errors)
        return overrides

    def _parse_text(self, param, errors):
        raw = self.params.get(param)
        if raw is None:
            return None

        value = raw.strip()
        if not value:
            errors[param] = 'Must not be blank.'
            return None

        limit = MAX_LENGTHS[param]
        if len(value) > limit:
            errors[param] = f'Must be at most {limit} characters.'
            return None
        return value

    def _check_domain(self, value, field):
        low, high = DOMAINS[field]
        if not low <= value <= high:
            return None, f'Must be between {low} and {high}.'
        return value, None
