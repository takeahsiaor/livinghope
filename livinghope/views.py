# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from livinghope.models import SermonSeries, Sermon, Author, BannerImage
from livinghope.models import Missionary, Leader, SmallGroup, Service
from livinghope.models import PrayerMeeting, Location
from livinghope.forms import PrayerForm, ContactForm
import math

def queryset_to_rows(queryset, num_cols):
    """
    helper function that accepts a queryset and returns
    the objects in the queryset broken up into rows
    of num_cols
    returns [row[obj, obj, obj...], [...]]
    """
    #stupid way of doing this
    #divide series into groups of three
    temp_holder = []
    all_objects_list = list(queryset) #force evaluation
    #below of hte form [row[series, series, series], [...]]
    all_objects_in_rows = []
    while all_objects_list:
        temp_holder.append(all_objects_list.pop(0))
        if len(temp_holder) == num_cols or not all_objects_list:
            all_objects_in_rows.append(temp_holder)
            temp_holder = []
    return all_objects_in_rows

def home(request):
    banner_images = BannerImage.objects.all().order_by('order')
    context = {'banner_images': banner_images}
    return render(request, 'home.html', context)

def missionaries(request):
    missionaries = Missionary.objects.all().order_by('last_name')
    rows_of_missionaries = queryset_to_rows(missionaries, 3)
    context = {'rows_of_missionaries': rows_of_missionaries}
    return render(request, 'missionaries.html', context)

def missionary_profile(request, missionary_id):
    try:
        missionary = Missionary.objects.get(id=missionary_id)
    except: #add specific exception later
        raise Http404
    context = {'missionary': missionary}
    return render(request, 'missionary_profile.html', context)

def leaders(request):
    #ORDER BY ORDER!!!!!
    leaders = Leader.objects.filter(active=True).order_by('order','last_name')
    #get leaders into rows of two
    #depending on formatting, maybe don't need rows
    #consider modal? just thumnails of htem and then ajax modal 
    #for details??
    rows_of_leaders = queryset_to_rows(leaders, 2)
    context = {'rows_of_leaders': rows_of_leaders}
    return render(request, 'leaders.html', context)

def sermon_series(request, series_id=None):
    all_series = SermonSeries.objects.all().order_by('-start_date')
    if series_id: #this is if a sermon series was selected
        try:
            series = SermonSeries.objects.get(id=int(series_id))
        except ObjectDoesNotExist:
            raise Http404
        sermons = series.sermon_set.all().order_by('-sermon_date')
        context = {'sermons': sermons,
                    'all_series': all_series,
                    'series':series,}
        return render(request, 'sermons.html', context)
    else: #this is to display all sermon series
        all_series_in_rows = queryset_to_rows(all_series, 3)

        context = {'all_series_in_rows': all_series_in_rows}
        return render(request, 'sermon_series.html', context)

class Prayer(FormView):
    template_name = 'prayer_form.html'
    form_class = PrayerForm
    success_url = reverse_lazy('prayer')

    def get_context_data(self, **kwargs):
        context = super(Prayer, self).get_context_data(**kwargs)
        context['prayer_meetings'] = PrayerMeeting.objects.all()
        return context

    def form_valid(self, form):
        form.send_prayer_email()
        success_message = "Thanks for submitting your prayer request! \
                            We will be praying!"

        messages.success(self.request, success_message)
        return super(Prayer, self).form_valid(form)

class Contact(FormView):
    template_name = 'contact_form.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def get_context_data(self, **kwargs):
        context = super(Contact, self).get_context_data(**kwargs)
        context['locations'] = Location.objects.filter(church=True)
        return context

    def form_valid(self, form):
        form.send_contact_email()
        success_message = "Thanks for submitting your message!"
        messages.success(self.request, success_message)
        return super(Contact, self).form_valid(form)


def statement_of_faith(request):
    return render(request, 'statement_of_faith.html')

def services(request):
    services = Service.objects.all()
    context = {'services':services}
    return render(request, 'services.html', context)

def ministries(request):
    #maybe put in sunday school classes and stuff here?
    return render(request, 'ministries.html')