"""Movie Form"""

from tw.forms import (TableForm, CalendarDatePicker,
    SingleSelectField, Spacer, TextField, TextArea)


class MovieForm(TableForm):

    hover_help = True

    genre_options = enumerate((
        'Action & Adventure', 'Animation', 'Comedy',
        'Documentary', 'Drama', 'Sci-Fi & Fantasy'))

    fields = [
        TextField('title', label_text='Movie Title',
            help_text='Please enter the full title of the movie.'),
        Spacer(),
        TextField('year', size=4,
            help_text='Please enter the year this movie was made.'),
        CalendarDatePicker('release_date', date_format='%y-%m-%d',
            help_text='Please pick the exact release date.'),
        SingleSelectField('genre', options=genre_options,
            help_text = 'Please choose the genre of the movie.'),
        Spacer(),
        TextArea('description', attrs=dict(rows=3, cols=25),
            help_text = 'Please provide a short description of the plot.'),
        Spacer()]

    submit_text = 'Save Movie'


create_movie_form = MovieForm("create_movie_form")
