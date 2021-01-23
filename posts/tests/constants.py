import tempfile
from django.urls import reverse


USERNAME = 'other'
USERNAME_AUTHOR = 'author'
SLUG = 'test_slug'
ABOUT_AUTHOR_URL = '/about/author/'
ABOUT_TECH_URL = '/about/tech/'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
GROUP_URL = reverse('group', args=[SLUG])
PROFILE_URL = reverse('profile', args=[USERNAME])
PROFILE_AUTHOR_URL = reverse('profile', args=[USERNAME_AUTHOR])
ERROR500_URL = reverse('error500')
ERROR400_URL = reverse('error404')

IMAGE_URL = 'posts/small.gif'
MEDIA_ROOT = tempfile.mkdtemp()

SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
             )
