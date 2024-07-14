# Project Title

Social Media a where users share one song of their choice per day.

## Description

TuneLink is an innovative web application developed using Django, designed to provide seamless connectivity and functionality. This Django app is connected with a PostgreSQL database to securely store and manage models created by Django, including Users, Profiles, and Posts. It leverages the Spotify Developer API to fetch accurate song and artist data whenever a user makes a post. It also uses JavaScript to create asynchronous functions that send data to the backend without requiring a full page refresh. To see all technologies used see more in the Built With section.

TunkLink is hosted on a cloud web hosting service called Render. Please note I am using the free version of their web instance and database so things may take a little while to load.

### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* Django
* Javascript
* HTML/CSS/BOOTSTRAP
* Spotify Developer API
* AJAX/Jquery
* PostgreSQL
* Whitenoise
* Hosted on Render

### Spotify API
As stated previously I used the Spotify Web API for Developers. For Tunelink I chose the Client Credentials Flow path, which does not include authorization, so information about users can not be accessed. In api.py, I have helper api functions to do all the heavy lifting. They get called in the upload view in views.py. Which then saves all the data from the json response I need to make a post. The only tricky thing about this is when you host it on the web you need to make sure it generates a new token everytime. Not only that but it seems to fail sometimes anyway from a "too many requests" error, so the best way I found to combat this was to implement a for loop to attempt a new token and request every time but make it wait 1 second before requesting. I recommend if you want to host a project like this you do the same unless you find a better more time effecient way.

### Dependencies

See requirements.txt
pip install everything there


### Static Files
Static Files can be quite tricky when hosting your website on the web, here are the issues I ran into and how I fixed them.
When running a website locally on your machine, Django takes care of the static files and media files. However when you decide to host it on the web it will no longer do this. The package I used to fix this is WhiteNoise. The version I used is in requirements.txt. If you have a folder called static inside your main directory use this code. When in production, so when debug is false, it makes whitenoise compress and store the static files because Django will no longer apply and serve them for you. Remind yourself you also need to put WhiteNoise in your middleware (see my settings.py for code).
```
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
if not DEBUG:
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Async Funcstions

One problem I ran into is when I implemented liking posts, following users, or really any time you send a request you need to reload the page. This isn't a very user friendly experience. Django doesn't have much of any built in support for this so I relied on AJAX to run asynchronous Javascript functions to update the like and follow counts without needing a page refresh so the user can keep its place on the webpage without an abrupt redirect. It allowed me to do that while still sending the data to the views/database to be updated and saved.
```
$(document).on('submit','#like-form',function(e){
            e.preventDefault();
            var post_id = $(this).data('post-id')
            $.ajax({
                type:'POST',
                url:"/like-post?post_id="+post_id,
                data:{
                    csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function(response){//Write function!}
```
e.preventDefault() is what prevents the webpage from refreshing. As you can see AJAX then makes a post request to the url and its view. In the success function you can write whatever you need to change about the webpage to make it responsive.

## Authors

ex. Collin Shuey  
ex. [@CollinShuey](https://github.com/CollinShuey)


