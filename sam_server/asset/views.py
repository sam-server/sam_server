import uuid
from django.http import JsonResponse

from ext_utils.json import partial_json_response

from authentication.models import User

from .models import Asset
from .resources import AssetResource, AssetListResource

ASSET_RESOURCE = AssetResource()
ASSET_LIST_RESOURCE = AssetListResource()


def asset(request, user_id=None, asset_id=None):

    try:
        asset = Asset.objects.filter(user=user_id, id=asset_id).get()
    except Asset.DoesNotExist:
        return JsonResponse({'error': 'Does not exist'}, status=404)

    if request.method == 'GET':
        return partial_json_response(request, ASSET_RESOURCE.to_json(asset))
    elif request.method == 'PUT':
        ## update an asset
        raise NotImplementedError()
    else:
        raise NotImplementedError()


def query_asset(request):
    id = request.GET.get('id')
    print('ID: {0}'.format(id))
    if id is not None:
        asset = Asset.objects.get(id=id)
        print(request)
        return partial_json_response(request, ASSET_RESOURCE.to_json(asset))


def list_user_assets(request, user_id):
    if request.method == 'GET':
        try:
            user = User.objects.filter(pk=user_id).get()
        except User.DoesNotExist:
            return JsonResponse({'error': 'no such user'}, status=404)
        ## TODO: Pagination
        user_assets = Asset.objects.filter(user=user).all()
        json_assets = ASSET_LIST_RESOURCE.to_json(dict(
            user_id=user.id,
            next_page_token=uuid.uuid4(),
            assets=user_assets
        ))
        print(json_assets)
        return partial_json_response(request, json_assets)

    elif request.method == 'POST':
        ## Create an object
        raise NotImplementedError()






