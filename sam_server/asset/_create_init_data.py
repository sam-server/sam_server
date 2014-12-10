"""
Temporary for use during early development, creates an asset
in the test database

TODO: DELETE ME
"""

from authentication.models import User
from .models import Asset

try:
    user = User.objects.get_by_natural_key(User.Type.BASIC, 'test_user')
except User.DoesNotExist:
    raise EnvironmentError('Need to create test user data before running script')

asset = Asset(
    qr_code='namespace={0};user={1}'.format('http://example.com', user.id),
    user=user,
    name='test_asset',
    description='An asset for use in testing'
)
asset.save()





