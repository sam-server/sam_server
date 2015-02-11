import json
import uuid
import io

from django.http import JsonResponse, HttpResponseNotAllowed
from django.core.context_processors import csrf
from django.core.files import File

from ext_utils.json import partial_json_response
from ext_utils.html import render

from authentication.decorators import authorization_required

from .models import Asset, HOST_URI
from .resources import AssetResource, AssetListResource


ASSET_RESOURCE = AssetResource()
ASSET_LIST_RESOURCE = AssetListResource()


@authorization_required
def update_or_view(request, asset_id):
    try:
        asset = Asset.objects.filter(id=asset_id).get()
    except Asset.DoesNotExist:
        return JsonResponse({'error': 'Does not exist'}, status=404)

    if request.method == 'GET':
        return get_asset(request, asset)
    elif request.method == 'PUT':
        return update_asset(request, asset)
    elif request.method == 'DELETE':
        return delete_asset(request, asset)
    else:
        return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])


@authorization_required
def list(request):
    if request.method == 'GET':
        return list_assets(request)
    elif request.method == 'POST':
        return create_asset(request)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


@authorization_required
def create(request):
    if request.method == 'GET':
        new_id = uuid.uuid4().hex
        resource = {
            'asset_id': new_id,
            'qr_code': HOST_URI + '/asset/{0}'.format(new_id)
        }
        data = {'resource': resource}
        data.update(csrf(request))
        return render('asset/create_asset.html', data)
    elif request.method == 'POST':
        return create_asset(request)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


def get_asset(request, asset):
    request_format = request.GET.get('format', 'document')
    if request_format.lower() == 'json':
        return partial_json_response(request, asset)
    else:
        json_asset = json.dumps(ASSET_RESOURCE.to_json(asset))
        render_data = {'resource': json_asset}
        render_data.update(csrf(request))
        return render('asset/asset.html', render_data)


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
    if 'image' in resource:
        if resource['image']:
            image = resource['image'][0]
            image_file = File(io.BytesIO(image.body_bytes))
            asset.image.save(image.name, image_file, save=False)
        else:
            ## Clear the image
            asset.image.delete(save=False)
    if 'use' in resource:
        asset.use = resource['use']
    if 'model_number' in resource:
        asset.model_number = resource['model_number']
    asset.save()
    return partial_json_response(request, ASSET_RESOURCE.to_json(asset))


def delete_asset(request, asset):
    asset.deleted = True
    asset.save()
    return JsonResponse({'deleted': True}, status=200)


def list_assets(request):
    """
    List all assets for the current user
    """
    user_assets = Asset.objects.filter(user=request.user, deleted=False).all()

    json_assets = ASSET_LIST_RESOURCE.to_json(dict(
        user_id=request.user.id,
        next_page_token=uuid.uuid4(),
        assets=user_assets
    ))
    request_format = request.GET.get('format', '')
    if request_format.lower() == 'json':
        return partial_json_response(request, json_assets)
    else:
        render_data = {'resource': json.dumps(json_assets)}
        render_data.update(csrf(request))
        return render('index.html', render_data)


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
        price=resource['price'],
        use=resource['use'] or '',
        model_number=resource['model_number'] or ''
    )
    if 'image' in resource and resource['image']:
        image = resource['image'][0]
        image_file = File(io.BytesIO(image.body_bytes))
        asset.image.save(image.name, image_file, save=False)

    asset.save()
    response = partial_json_response(request, ASSET_RESOURCE.to_json(asset))
    return response







