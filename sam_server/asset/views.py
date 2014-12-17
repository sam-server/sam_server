import uuid
from django.http import JsonResponse, HttpResponseNotAllowed
from django.core.context_processors import csrf

from ext_utils.json import partial_json_response
from ext_utils.html import render

from authentication.models import User
from authentication.decorators import authorization_required

from .models import Asset
from .resources import AssetResource, AssetListResource


ASSET_RESOURCE = AssetResource()
ASSET_LIST_RESOURCE = AssetListResource()


@authorization_required
def asset(request, user_id=None, asset_id=None):

    try:
        asset = Asset.objects.filter(user=user_id, id=asset_id).get()
    except Asset.DoesNotExist:
        return JsonResponse({'error': 'Does not exist'}, status=404)

    resource = ASSET_RESOURCE.to_json(asset)
    if request.method == 'GET':
        request_format = request.GET.get('format')
        if request_format == 'json':
            return partial_json_response(request, resource)
        else:
            resource.update(csrf(request))
            return render('asset/asset.html', resource)
    elif request.method == 'PUT':
        return update_asset(request, asset)
    else:
        return HttpResponseNotAllowed(['GET', 'PUT'])


def update_asset(request, asset):
    if request.JSON is None:
        return JsonResponse({'error': 'Expected JSON content'}, status=400)
    try:
        resource = ASSET_RESOURCE.to_python(request.JSON)
    except ValueError as e:
        ## TODO: Make a ResourceError which includes information
        ## about the valid fields as a json response
        return JsonResponse({'error': str(e)}, status=400)

    if 'name' in resource:
        asset.name = resource['name']
    if 'description' in resource:
        asset.description = resource['description']
    if 'price' in resource:
        asset.price = resource['price']
    asset.save()
    return partial_json_response(request, ASSET_RESOURCE.to_json(asset))


@authorization_required
def create_asset(request):
    if request.JSON is None:
        return JsonResponse({'error', 'Expected JSON body'}, status=400)
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        resource = ASSET_RESOURCE.to_python(request.JSON)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


    if 'name' not in resource or not resource['name']:
        return JsonResponse({'error': 'Invalid name for resource'})

    asset = Asset(
        user=request.user,
        name=resource['name'],
        description=resource['description'] or '',
        price=resource['price']
    )
    asset.save()
    return partial_json_response(request, ASSET_RESOURCE.to_json(asset))







def query_asset(request):
    id = request.GET.get('id')
    if id is not None:
        asset = Asset.objects.get(id=id)
        return partial_json_response(request, ASSET_RESOURCE.to_json(asset))


@authorization_required
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
        return partial_json_response(request, json_assets)

    elif request.method == 'POST':
        ## Create an object
        raise NotImplementedError()






