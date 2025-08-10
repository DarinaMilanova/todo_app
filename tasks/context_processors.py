def dark_mode(request):
    return {'dark_mode': request.session.get('dark_mode', False)}