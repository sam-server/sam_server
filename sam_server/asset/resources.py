
from ext_utils.json.resources import *

from common.resources import MoneyAmountResource


class AssetResource(ModelResource):
    KIND = 'assets#asset'

    id = UUIDResource()
    user_id = IntegerResource()
    qr_code = StringResource()
    name = StringResource()
    description = StringResource()
    use = StringResource()
    model_number = StringResource()
    price = MoneyAmountResource(required=False)
    date_purchased = DateTimeResource(required=False)

    image_src = StringResource(required=False)
    ## The resource to upload the file
    image = FileResource(required=False)

    def get_user_id(self, model):
        return model.user.id

    def get_image_src(self, model):
        if not model.image:
            return None
        return model.image.url

    def get_image(self, model):
        return None


class AssetListResource(ModelResource):
    KIND = 'assets#assets'

    next_page_token = UUIDResource()
    user_id = IntegerResource()
    assets = ListResource(item_resource=AssetResource())


class AssetAttachmentResource(ModelResource):
    KIND = 'asset#attachment'

    name = StringResource()
    asset = UUIDResource()

    def get_asset(self, model):
        return model.asset.id


