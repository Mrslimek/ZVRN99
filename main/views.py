from django.shortcuts import render
from django.contrib import messages
from .forms import JSONUploadForm
from .models import ReceivedDataORM
from .services import process_upload_file


def root(request):
    form = JSONUploadForm()
    if request.method == "POST":
        form = JSONUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.cleaned_data["file"]
            model_instances, errors = process_upload_file(file_obj=file_obj)
            if errors:
                for error in errors:
                    form.add_error("file", error)
            else:
                ReceivedDataORM.objects.bulk_create(model_instances)
                messages.success(request, "Данные успешно сохранены")
                return render(request, "index.html", {"form": form})
    return render(request, "upload_form.html", {"form": form})


def data_table(request):
    data = ReceivedDataORM.objects.all()
    context = {"data": data}
    return render(request, "data_table.html", context)
