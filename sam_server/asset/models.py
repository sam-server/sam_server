from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.db import models
from common.models import ModelBase

from common.currency import MoneyAmount
from authentication.models import User

try:
    HOST_URI = getattr(settings, 'HOST_URI')
except AttributeError:
    raise ImproperlyConfigured('asset module requires HOST_URI to be configured'
                               'in the global settings')

class AssetManager(models.Manager):
    def get_by_qr_code(self, qr_code):
        return self.get(qr_code=qr_code)

    def all_assets_for_user(self, user):
        return self.filter(user=user).all()

    def create_asset(self, user, **kwargs):
        """
        Creates a new asset for the given user.
        A qr code will be automatically generated
        """
        asset = Asset(user=user, **kwargs)


def _asset_image_upload_location(asset, filename):
    return 'assets/{0}/images/{1}'.format(asset.id, filename)


class Asset(ModelBase):

    ## The owner of the asset.
    user = models.ForeignKey(User)

    objects = AssetManager()

    # A human readable description of the asset
    name = models.CharField(max_length=128)

    description = models.CharField(max_length=1024)

    use = models.CharField(max_length=256)

    model_number = models.CharField(max_length=128)

    vendor = models.CharField(max_length=128)

    ## The price of the item as an integer
    price_value = models.IntegerField(null=True)

    ## The ISO currency code of the price.
    price_currency_code = models.CharField(max_length=3)

    date_purchased = models.DateField(null=True)

    image = models.FileField(
        max_length=1024,
        upload_to=_asset_image_upload_location,
        blank=True,
        null=True
    )

    deleted = models.BooleanField(default=False)

    def _get_price(self):
        if not self.price_currency_code:
            return None
        return MoneyAmount(self.price_currency_code, self.price_value)

    def _set_price(self, value):
        if not isinstance(value, MoneyAmount):
            raise TypeError('Not a money amount')
        self.price_currency_code = value.code
        self.price_value = value.value

    price = property(_get_price, _set_price)

    def get_absolute_url(self):
        return '/asset/{0}'.format(self.id.hex)

    @property
    def qr_code(self):
        return HOST_URI + self.get_absolute_url()


class AssetAttachement(ModelBase):
    asset = models.ForeignKey(Asset)

    name = models.CharField(max_length=128)
    ## The mime type of the attachment
    type = models.CharField(max_length=64)

    location = models.FilePathField()

    upload_date = models.DateField(auto_now=True)


