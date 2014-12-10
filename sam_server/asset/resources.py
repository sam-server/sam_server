
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

    def get_user_id(self, model):
        return model.user.id


class AssetListResource(ModelResource):
    KIND = 'assets#assets'

    next_page_token = UUIDResource()
    user_id = IntegerResource()
    assets = ListResource(item_resource=AssetResource())




