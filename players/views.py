import json

from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from players import service
from players.exceptions import PlayerNotFound, ValidationError
from players.serializers import PlayerSerializer


def _errors(errors, status=400):
    return JsonResponse({'errors': errors}, status=status)


def _not_found(exc):
    return _errors({'id': str(exc)}, status=404)


def _json_body(request):
    if not request.body:
        return None, _errors({'body': 'Request body is empty.'})
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return None, _errors({'body': 'Request body is not valid JSON.'})
    if not isinstance(payload, dict):
        return None, _errors({'body': 'Request body must be a JSON object.'})
    return payload, None


@method_decorator(csrf_exempt, name='dispatch')
class PlayerListView(View):
    def get(self, request):
        try:
            players, total = service.list_players(request.GET)
        except ValidationError as exc:
            return _errors(exc.errors)

        return JsonResponse({
            'data': [PlayerSerializer.to_representation(player) for player in players],
            'meta': {'count': len(players), 'total': total},
        })

    def post(self, request):
        payload, error = _json_body(request)
        if error:
            return error
        try:
            player = service.create_player(payload)
        except ValidationError as exc:
            return _errors(exc.errors)

        return JsonResponse({'data': PlayerSerializer.to_representation(player)}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class RandomPlayerView(View):
    """Preview only — the generated player is not saved."""

    def get(self, request):
        try:
            player = service.preview_random_player(request.GET)
        except ValidationError as exc:
            return _errors(exc.errors)

        return JsonResponse({'data': player})


@method_decorator(csrf_exempt, name='dispatch')
class PlayerDetailView(View):
    def get(self, request, player_id):
        return self._render(player_id)

    def put(self, request, player_id):
        return self._update(request, player_id, partial=False)

    def patch(self, request, player_id):
        return self._update(request, player_id, partial=True)

    def delete(self, request, player_id):
        try:
            player = service.get_player(player_id)
        except PlayerNotFound as exc:
            return _not_found(exc)

        service.delete_player(player)
        return HttpResponse(status=204)

    def _render(self, player_id):
        try:
            player = service.get_player(player_id)
        except PlayerNotFound as exc:
            return _not_found(exc)

        return JsonResponse({'data': PlayerSerializer.to_representation(player)})

    def _update(self, request, player_id, partial):
        try:
            player = service.get_player(player_id)
        except PlayerNotFound as exc:
            return _not_found(exc)

        payload, error = _json_body(request)
        if error:
            return error
        try:
            player = service.update_player(player, payload, partial)
        except ValidationError as exc:
            return _errors(exc.errors)

        return JsonResponse({'data': PlayerSerializer.to_representation(player)})
