from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Product,
    convertUnit,
    Unit,
    ProductTransaction,
    PriceReference,
    ProductCategory,
)
from utils.forms import CategoryCreateForm as BaseCategoryCreateForm
from utils.forms import OrderCreateForm as BaseOrderCreateForm
from django.forms import HiddenInput

from users.models import (
    Associated,
)
from utils.models import (
    Order,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText, AppendedText, PrependedAppendedText
from django.utils.translation import gettext_lazy as _


class OrderCreateForm(BaseOrderCreateForm):
    href = "{% url 'select-provider' %}?next={{ request.path|urlencode }}"
    tooltip = "Modify provider"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['associated'].label = _("Provider")
        self.fields['badge'].widget = HiddenInput()


class CommonTransactionLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            Div(
                Div(
                    Field(
                        PrependedText('price', '$')
                    ),
                    css_class="col-6"
                ),
                Div(
                    Div(
                        AppendedText('tax', '%'),
                    ),
                    css_class="col-6"
                ),
                css_class="row mb-3"
            ),
            Div(
                Div(
                    Field('quantity'
                          ),
                    css_class="col-4"
                ),
                Div(
                    Div(
                        Field('unit',
                              css_class="form-select")
                    ),
                    css_class="col-8"
                ),
                css_class="row mb-3"
            ),
            Div(
                Div(
                    Field('note', rows='2')
                ),
                css_class="mb-3"
            )
        )


class TransactionCreateForm(forms.ModelForm):

    class Meta:
        model = ProductTransaction
        fields = (
            'price',
            'note',
            'quantity',
            'unit',
            'tax'
        )

    def clean_tax(self):
        tax = self.cleaned_data['tax']
        if tax is None:
            tax = 0
        return tax

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if self.order.type == "sell":
            error_msg = ""
            unit = Unit.objects.get(id=int(self.data['unit']))
            available = self.product.computeAvailable(self.id)
            # Compute the available quantity in transaction unit
            available = convertUnit(self.product.unit, unit, available)
            if available < quantity:
                if int(available) == float(available):
                    decimals = 0
                else:
                    decimals = 2  # Assumes 2 decimal places
                error_msg += F'The quantity cannot be higher than {available:.{decimals}f}{unit}.'
                raise ValidationError(error_msg)
        return quantity

    def clean_price(self):
        price = self.cleaned_data['price']
        if self.order.type == "sell":
            error_msg = ""
            unit = Unit.objects.get(id=int(self.data['unit']))
            # Compute the price in product unit
            product_cost = price / convertUnit(unit, self.product.unit, 1)
            cost = self.product.getCost()
            average = F" Cost: ${cost:.2f}."
            if unit != self.product.unit:
                error_msg += F'${price:.2f} for one {unit} implies ${product_cost:.2f} each {self.product.unit}. ' + average
            if product_cost < self.product.min_price:
                error_msg += F'The price cannot be lower than ${self.product.min_price:.2f}.' + average
                raise ValidationError(error_msg)
        return price

    def __init__(self, *args, **kwargs):
        if 'product' in kwargs:
            self.product = kwargs['product']
            kwargs.pop('product')
        else:
            self.product = None
        if 'id' in kwargs:
            self.id = kwargs['id']
            kwargs.pop('id')
        else:
            self.id = None
        if 'order' in kwargs:
            self.order = kwargs['order']
            kwargs.pop('order')
        else:
            self.order = None
        super().__init__(*args, **kwargs)
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({'autofocus': 'autofocus'})
            break

        # Price
        minimum = F"Minimum: ${self.product.min_price:.2f}/{self.product.unit}."
        cost = self.product.getCost()
        average = F" Cost: ${cost:.2f}/{self.product.unit}."
        self.fields['price'].help_text = minimum + average

        # Quantity
        available = self.product.computeAvailable(self.id)
        if int(available) == float(available):
            decimals = 0
        else:
            decimals = 2  # Assumes 2 decimal places for money
        self.fields['quantity'].help_text = F"Available: {available:.{decimals}f}{self.product.unit}."

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = 'form-label'
        self.helper.add_input(Submit("submit", "Save"))
        self.helper.layout = Layout(
            CommonTransactionLayout()
        )


class TransactionProviderCreateForm(TransactionCreateForm):
    associated = forms.fields_for_model(Order)['associated']

    class Meta:
        model = ProductTransaction
        fields = (
            'price',
            'note',
            'quantity',
            'unit',
            'tax',
            'associated'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            CommonTransactionLayout(),
            Div(
                Div(
                    Field(
                        PrependedText('associated',
                                      '<i class="bx bx-user-circle"></i>',
                                      css_class="form-select")
                    ),
                    css_class="col-10"
                ),
                Div(
                    HTML(
                        """
                    <a class="btn btn-icon btn-outline-primary position-absolute bottom-0"
                       type="button"
                       href="{% url 'create-provider' %}?next={{ request.path|urlencode }}">
                        <span class="tf-icons bx bx-plus"></span>
                    </a>
                    """),
                    css_class="col-2 position-relative"
                ),
                css_class="row mb-3"
            ),
        )


class CategoryCreateForm(BaseCategoryCreateForm):

    class Meta:
        model = ProductCategory
        fields = ('name', 'icon',)


class UnitCreateForm(forms.ModelForm):

    class Meta:
        model = Unit
        fields = ('name',
                  'factor',
                  'magnitude')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({'autofocus': 'autofocus'})
            break

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = 'form-label'
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('name')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field('factor')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field('magnitude')
                ),
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class PriceReferenceCreateForm(forms.ModelForm):

    class Meta:
        model = PriceReference
        fields = ('store',
                  'url',
                  'price')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({'autofocus': 'autofocus'})
            break

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = 'form-label'
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('store')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field('url')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field(PrependedText('price', '$')
                          ),
                    css_class="mb-3"
                )
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class ProductCreateForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ('name',
                  'image',
                  'description',
                  'unit',
                  'category',
                  'type',
                  'sell_tax',
                  'suggested_price',
                  'min_price',
                  'quantity_min',
                  'active')

    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            kwargs.pop('title')
        else:
            self.title = _("Create Product")

        super().__init__(*args, **kwargs)
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({'autofocus': 'autofocus'})
            break

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = 'form-label'
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        self.title,
                        Div(
                            Div(
                                Field('name')
                            ),
                            css_class="mb-3"
                        ),
                        HTML(
                            """
                            <img id="preview"
                            {% if form.image.value %}
                                class="img-responsive"
                                src="/media/{{ form.image.value }}"
                            {% endif %}">
                            """
                        ),
                        Div(
                            Div(
                                Field('image', css_class="form-select")
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field('description', rows='2')
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field('unit', css_class="form-select")
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field('category', css_class="form-select")
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field('type', css_class="form-select")
                            ),
                            css_class="mb-3"
                        ),
                        css_class="card-body"
                    ),
                    css_class="card mb-4"
                ),
                css_class="col-xxl"
            ),

            Div(
                Div(
                    Fieldset(
                        _("Advance configuration"),
                        Div(
                            Div(
                                Field('active')
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field('quantity_min', css_class="form-select")
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field(
                                    AppendedText('suggested_price', '%')
                                )
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field(
                                    PrependedText('min_price', '$')
                                )
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field(
                                    AppendedText('sell_tax', '%')
                                )
                            ),
                            css_class="mb-3"
                        ),
                        ButtonHolder(
                            Submit('submit', 'Enviar',
                                   css_class='btn btn-success')
                        ),
                        css_class="card-body"
                    ),
                    css_class="card mb-4"
                ),
                css_class="col-xxl"
            )
        )
