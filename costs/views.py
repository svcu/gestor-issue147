from .models import Cost, CostCategory
from django.urls import reverse_lazy
from django.views.generic.edit import (
    UpdateView,
    CreateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required
from .forms import CategoryCreateForm, CostsCreateForm, CostsUpdateForm
from django.utils.translation import gettext_lazy as _
from gestor.views.utils import getMonthYear
from datetime import datetime

# -------------------- Category ----------------------------


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = CostCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-costs-category')


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = CostCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-costs-category')


class CategoryListView(LoginRequiredMixin, ListView):
    model = CostCategory
    template_name = 'costs/category_list.html'


@login_required
def delete_category(request, id):
    # fetch the object related to passed id
    category = get_object_or_404(CostCategory, id=id)
    category.delete()
    return redirect('list-costs-category')

# -------------------- Costs ----------------------------


@login_required
def create_cost(request):
    form = CostsCreateForm()
    if request.method == 'POST':
        form = CostsCreateForm(request.POST, request.FILES)
        if form.is_valid():
            cost = form.save(commit=False)
            cost.created_by = request.user
            cost.save()
            return redirect('list-cost')
    context = {
        'form': form,
        'title': _('Create cost')
    }
    return render(request, 'costs/cost_create.html', context)


@login_required
def update_cost(request, id):
    # fetch the object related to passed id
    cost = get_object_or_404(Cost, id=id)
    # pass the object as instance in form
    form = CostsUpdateForm(request.POST or None, request.FILES or None,
                           instance=cost)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('list-cost')

    # add form dictionary to context
    context = {
        'form': form,
        'title': _('Update cost')
    }

    return render(request, 'costs/cost_create.html', context)


@login_required
def list_cost(request, year=None, month=None):

    ((previousMonth, previousYear),
     (currentMonth, currentYear),
     (nextMonth, nextYear)) = getMonthYear(month, year)

    costs = Cost.objects.all().order_by("-date", "-id")
    costs = costs.filter(date__year=currentYear,
                         date__month=currentMonth)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date is not None:
        costs = costs.filter(date__gte=start_date)

    if end_date is not None:
        costs = costs.filter(date__lte=end_date)

    context = {
        'previousMonth': previousMonth,
        'currentMonth': currentMonth,
        'nextMonth': nextMonth,
        'thisMonth': datetime.now().month,
        'previousYear': previousYear,
        'currentYear': currentYear,
        'nextYear': nextYear,
        'thisYear': datetime.now().year,
        'interval': 'monthly',
        'costs': costs,
    }

    return render(request, 'costs/cost_list.html', context)


@login_required
def detail_cost(request, id):
    # fetch the object related to passed id
    cost = get_object_or_404(Cost, id=id)
    return render(request, 'costs/cost_detail.html', {'cost': cost})


@login_required
def delete_cost(request, id):
    # fetch the object related to passed id
    cost = get_object_or_404(Cost, id=id)
    cost.delete()
    return redirect('list-cost')
