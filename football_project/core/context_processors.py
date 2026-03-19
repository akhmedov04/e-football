from .models import PlayerRequest

def admin_context(request):
    ctx = {'user_role': None, 'pending_requests_count': 0}
    if request.user.is_authenticated:
        if request.user.is_superuser:
            ctx['user_role'] = 'superuser'
            ctx['pending_requests_count'] = PlayerRequest.objects.filter(status='pending').count()
        elif hasattr(request.user, 'region_admin_profile'):
            ctx['user_role'] = 'region_admin'
            region = request.user.region_admin_profile.region
            ctx['pending_requests_count'] = PlayerRequest.objects.filter(team__city__region=region, status='pending').count()
        elif hasattr(request.user, 'coach_profile'):
            ctx['user_role'] = 'coach'
            ctx['pending_requests_count'] = PlayerRequest.objects.filter(created_by=request.user, status='pending').count()
    return ctx
