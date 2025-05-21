from django.forms import Form, FileField


class JSONUploadForm(Form):
    """
    Форма, принимающая json файл в формате
    [
        {
        "name": "random string less than 50 characters",
        "date": "date string in YYYY-MM-DD_HH:mm format"
        },
        ...
    ]
    """

    file = FileField()
