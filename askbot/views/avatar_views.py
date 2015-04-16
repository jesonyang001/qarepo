from avatar.conf import settings as avatar_settings
from avatar.forms import PrimaryAvatarForm, UploadAvatarForm
from avatar.models import Avatar
from avatar.signals import avatar_updated
from askbot.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
import functools

def admin_or_owner_required(func):
    """decorator that allows admin or account owner to
    call the view function"""
    @functools.wraps(func)
    def wrapped(request, user_id=None):
        if request.user.is_authenticated():
            if request.user.is_administrator() or request.user.id == user_id:
                return func(request, user_id)
        #delegate to do redirect to the login_required
        return login_required(func)(request, user_id)
    return wrapped


def get_avatar_data(user, avatar_size):
    """avatar data and boolean, which is true is user has custom avatar
    avatar data is a list of dictionaries, one for each avatar with keys:
    * id - avatar id (this field is missing for gravatar and default avatar)
    * avatar_type (string , 'uploaded_avatar', 'gravatar', 'default_avatar')
    * url (url to avatar of requested size)
    * is_primary (True if primary)
    Primary avatar data must be first in the list.
    There will always be only one primary_avatar.
    List includes gravatar, default avatar and any uploaded avatars.
    """
    #determine avatar data for the view
    avatar_data = list()
    avatars = user.avatar_set.all()
    #iterate through uploaded avatars
    for avatar in avatars:
        datum = {
            'id': avatar.id,
            'avatar_type': 'uploaded_avatar',
            'url': avatar.avatar_url(avatar_size),
            'is_primary': avatar.primary
        }
        avatar_data.append(datum)

    #add gravatar datum
    gravatar_datum = {
        'avatar_type': 'gravatar',
        'url': user.get_gravatar_url(avatar_size),
        'is_primary': (user.avatar_type == 'g')
    }
    avatar_data.append(gravatar_datum)

    #add default avatar datum
    default_datum = {
        'avatar_type': 'default_avatar',
        'url': user.get_default_avatar_url(avatar_size),
        'is_primary': (user.avatar_type == 'n')
    }
    avatar_data.append(default_datum)

    #if there are >1 primary avatar, select just one
    primary_avatars = filter(lambda v: v['is_primary'], avatar_data)
    #force just one primary avatar if there are >1
    if len(primary_avatars) > 1:
        gravatars = filter(
                        lambda v: v.type == 'gravatar',
                        primary_avatars
                    )

        def clear_primary(datum):
            datum['is_primary'] = False
        map(clear_primary, primary_avatars)

        if len(gravatars):
            gravatars[0]['is_primary'] = True
        else:
            primary_avatars[0]['is_primary'] = True
            
    #insert primary avatar first
    primary_avatars = filter(lambda v: v['is_primary'], avatar_data)
    if len(primary_avatars):
        primary_avatar = primary_avatars[0]
        avatar_data.remove(primary_avatar)
        avatar_data.insert(0, primary_avatar)

    can_upload = avatars.count() < avatar_settings.AVATAR_MAX_AVATARS_PER_USER
    return avatar_data, bool(avatars.count()), can_upload


def redirect_to_show_list(user_id):
    return HttpResponseRedirect(
        reverse('askbot_avatar_show_list', kwargs={'user_id': user_id})
    )
   

@admin_or_owner_required
def show_list(request, user_id=None, extra_context=None, avatar_size=128):
    """lists user's avatars, including gravatar and the default avatar"""
    user = get_object_or_404(User, pk=user_id)
    avatar_data, has_uploaded_avatar, can_upload = get_avatar_data(user, avatar_size)
    context = {
        'avatar_data': avatar_data,
        'has_uploaded_avatar': has_uploaded_avatar,
        'can_upload': can_upload,
        'page_class': 'user-profile-page',
        'upload_avatar_form': UploadAvatarForm(user=user),
        'view_user': user
    }
    context.update(extra_context or {})
    return render(request, 'avatar/show_list.html', context)

@admin_or_owner_required
def set_primary(request, user_id=None, extra_context=None, avatar_size=128):
    """changes default uploaded avatar"""
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        updated = False
        form = PrimaryAvatarForm(
                        request.POST,
                        user=user,
                        avatars=user.avatar_set.all()
                    )
        if 'choice' in request.POST and form.is_valid():
            avatar = Avatar.objects.get(id=form.cleaned_data['choice'])
            avatar.primary = True
            avatar.save()
            avatar_updated.send(sender=Avatar, user=request.user, avatar=avatar)
    return redirect_to_show_list(user_id)


@admin_or_owner_required
def upload(request, user_id=None):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST' and 'avatar' in request.FILES:
        form = UploadAvatarForm(
                        request.POST,
                        request.FILES,
                        user=user)
        if form.is_valid():
            avatar = Avatar(user=user, primary=True)
            image_file = request.FILES['avatar']
            avatar.avatar.save(image_file.name, image_file)
            avatar.save()
            avatar_updated.send(sender=Avatar, user=user, avatar=avatar)

    return redirect_to_show_list(user_id)


def delete(request, avatar_id):
    avatar = get_object_or_404(Avatar, pk=avatar_id)
    user = request.user
    if request.method == 'POST' \
        and user.is_authenticated() \
        and (user.is_administrator_or_moderator() \
            or avatar.user_id == user.id):
        avatar_type = avatar.user.avatar_type
        avatar.delete()
        avatar.user.avatar_type = avatar_type
        avatar.user.save()
        if avatar_type == 'g':
            avatar.user.avatar_set.update(primary=False)

    return redirect_to_show_list(avatar.user_id)


@admin_or_owner_required
def enable_gravatar(request, user_id=None):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        user.avatar_type = 'g'
        user.save()
        user.avatar_set.update(primary=False)
    return redirect_to_show_list(user_id)


@admin_or_owner_required
def enable_default_avatar(request, user_id=None):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        user.avatar_type = 'n'
        user.save()
        user.avatar_set.update(primary=False)
    return redirect_to_show_list(user_id)


@admin_or_owner_required
def disable_gravatar(request, user_id=None):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        user.avatar_type = 'a'
        user.save()
        if user.avatar_set.count():
            avatar = user.avatar_set.all()[0]
            avatar.primary = True
            avatar.save()
            avatar_updated.send(sender=Avatar, user=request.user, avatar=avatar)
    return redirect_to_show_list(user_id)
