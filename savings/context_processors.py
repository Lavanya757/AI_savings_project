def theme_preference(request):
    theme = request.COOKIES.get('theme', 'light')
    return {'theme_preference': theme}
