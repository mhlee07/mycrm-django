from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.core.paginator import Paginator, EmptyPage
from django.contrib import messages
from django.db.models import Sum, F
from .models import Profile, Customer, Order, Product
from .forms import UserCreationForm, ProfileForm, CustomerForm, ProductForm, OrderForm
from .filters import OrderFilter, ProductFilter
from .decorators import unauthenticated_user


# User register
@unauthenticated_user
def user_register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Successfully created account for:  ' + username
                             + '. You are able to login.')
            return redirect('sales:login')
        else:
            messages.warning(request, form.errors)

    context = {'form': form}
    return render(request, 'sales/register.html', context)


# User login
@unauthenticated_user
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if user.profile.first_name is not None:
                return redirect('sales:index')
            else:
                return redirect('sales:profile-add')
        else:
            messages.warning(request, 'Username or Password is incorrect.')

    context = {}
    return render(request, 'sales/login.html', context)


# User logout
def user_logout(request):
    logout(request)
    return redirect('sales:login')


# User profile create
@login_required(login_url='sales:login')
def profile_create(request):
    profile = Profile.objects.get(pk=request.user.profile.id)
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            messages.success(request, 'Successfully created profile for:  '
                             + first_name + ' ' + last_name)
            return redirect('sales:index')

    context = {'form': form, 'title': 'Complete Profile Information'}
    return render(request, 'sales/profile-form.html', context)


# User profile view
@login_required(login_url='sales:login')
def profile_view(request, profile_id):
    profile = Profile.objects.get(pk=profile_id)

    if request.user.profile.id == profile_id:
        context = {'profile': profile}
        return render(request, 'sales/profile.html', context)
    else:
        messages.info(request, 'You are not authorized to view this page...')
        return redirect('sales:index')


# User profile update
@login_required(login_url='sales:login')
def profile_update(request, profile_id):
    profile = Profile.objects.get(pk=profile_id)

    if request.user.profile.id == profile_id:
        form = ProfileForm(instance=profile)

        if request.method == 'POST':
            form = ProfileForm(request.POST, instance=profile)

            if form.is_valid():
                form.save()
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                messages.success(request, 'Successfully updated profile for:  '
                                 + first_name + ' ' + last_name)
                return redirect('sales:index')

        context = {'form': form, 'title': 'Update Profile'}
        return render(request, 'sales/profile-form.html', context)
    else:
        messages.info(request, 'You are not authorized to view this page...')
        return redirect('sales:index')


# Data
@login_required(login_url='sales:login')
def data_view(request):
    sales_vs_day = Order.objects.order_by('order_date').values('order_date').annotate(
        total_sales=Sum(F('quantity') * F('product__price')))
    data_1 = []
    for obj in sales_vs_day:
        item = {
            'date': obj['order_date'],
            'daily_sales': obj['total_sales']
        }
        data_1.append(item)

    customer_vs_sales = Order.objects.order_by('-customer__id').values('customer__name').annotate(
        total_sales=Sum(F('quantity') * F('product__price')))
    data_2 = []
    for obj in customer_vs_sales:
        item = {
            'customer_name': obj['customer__name'],
            'sales_sum': obj['total_sales']
        }
        data_2.append(item)

    product_vs_quantity = Order.objects.order_by('product__id').values('product__name').annotate(
        sum=Sum('quantity'))
    data_3 = []
    for obj in product_vs_quantity:
        item = {
            'product_name': obj['product__name'],
            'quantity_sum': obj['sum']
        }
        data_3.append(item)

    context = {
        'data_1': data_1[-10:],
        'data_2': data_2,
        'data_3': data_3,
    }
    return JsonResponse(context, safe=False)


# Dashboard
@login_required(login_url='sales:login')
def home_view(request):
    order_list = Order.objects.all().order_by('-id')
    customer_list = Customer.objects.all().order_by('-id')

    # Customer search
    search_value = request.GET.get('q')
    if search_value != '' and search_value is not None:
        customer_list = customer_list.filter(name__icontains=search_value)

    # Pagination of customers
    p = Paginator(customer_list, 3)
    page_num1 = request.GET.get('page', 1)
    try:
        customer_list = p.page(page_num1)
    except EmptyPage:
        customer_list = p.page(1)

    # Pagination of orders
    p = Paginator(order_list, 5)
    page_num2 = request.GET.get('page', 1)
    try:
        order_list = p.page(page_num2)
    except EmptyPage:
        order_list = p.page(1)

    context = {
        'customer_list': customer_list,
        'order_list': order_list
    }
    return render(request, 'sales/index.html', context)


# View customer
@login_required(login_url='sales:login')
def customer_view(request, pk):
    customer = Customer.objects.get(pk=pk)

    if request.user.profile.id == customer.user_profile.id:

        order_list = customer.order_set.all().order_by('-id')
        total_price_sum = 0
        for order in order_list:
            total_price_sum += order.total_price()
        num_of_order = order_list.count()
        closed_order = order_list.filter(status='Delivered').count()
        order_in_progress = order_list.exclude(status='Delivered').count()

        # Order filter
        order_filter = OrderFilter(request.GET, queryset=order_list)
        order_list = order_filter.qs

        # Pagination of orders
        p = Paginator(order_list, 5)
        page_number = request.GET.get('page', 1)
        try:
            order_list = p.page(page_number)
        except EmptyPage:
            order_list = p.page(1)

        context = {
            'customer': customer,
            'order_list': order_list,
            'total_price_sum': total_price_sum,
            'num_of_order': num_of_order,
            'closed_order': closed_order,
            'order_in_progress': order_in_progress,
            'order_filter': order_filter,
        }
        return render(request, 'sales/detail.html', context)

    else:
        messages.info(request, 'You are not authorized to view this page...')
        return redirect('sales:index')


# Create customer
@login_required(login_url='sales:login')
def customer_create(request):
    profile = Profile.objects.get(pk=request.user.profile.id)
    form = CustomerForm()

    if request.method == 'POST':
        form = CustomerForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.user_profile = profile
            instance.save()
            customer_name = form.cleaned_data.get('name')
            messages.success(request, 'Successfully created customer:  ' + customer_name)
            return redirect('sales:index')

    context = {'form': form, 'profile': profile, 'title': 'Add a New Customer'}
    return render(request, 'sales/customer-form.html', context)


# Update customer
@login_required(login_url='sales:login')
def customer_update(request, pk):
    customer = Customer.objects.get(pk=pk)

    if request.user.profile.id == customer.user_profile.id:
        form = CustomerForm(instance=customer)

        if request.method == 'POST':
            form = CustomerForm(request.POST, instance=customer)

            if form.is_valid():
                form.save()
                customer_name = request.POST.get('name')
                messages.success(request, 'Successfully updated customer:  ' + customer_name)
                return HttpResponseRedirect(reverse('sales:detail', kwargs={'pk': customer.id}))

        context = {'form': form, 'title': 'Update Customer Information'}
        return render(request, 'sales/customer-form.html', context)
    else:
        messages.info(request, 'You are not authorized to view this page...')
        return redirect('sales:index')


# Delete customer
@login_required(login_url='sales:login')
def customer_delete(request, pk):
    customer = Customer.objects.get(pk=pk)

    if request.user.profile.id == customer.user_profile.id:
        if request.method == 'POST':
            customer.delete()
            messages.warning(request, str(customer) + ' has been deleted.')
            return redirect('sales:index')

        context = {'customer': customer}
        return render(request, 'sales/customer-delete.html', context)
    else:
        messages.info(request, 'You are not authorized to view this page...')
        return redirect('sales:index')


# View products
@login_required(login_url='sales:login')
def product_view(request):
    product_list = Product.objects.all().order_by('-id')
    product_filter = ProductFilter(request.GET, queryset=product_list)
    product_list = product_filter.qs

    # Pagination of products
    p = Paginator(product_list, 5)
    page_number = request.GET.get('page', 1)
    try:
        product_list = p.page(page_number)
    except EmptyPage:
        product_list = p.page(1)

    context = {
        'product_list': product_list,
        'product_filter': product_filter
    }
    return render(request, 'sales/product.html', context)


# Create product
@login_required(login_url='sales:login')
def product_create(request):
    form = ProductForm()

    if request.method == 'POST':
        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            product_name = form.cleaned_data.get('name')
            messages.success(request, 'Successfully created product:  ' + product_name)
            return redirect('sales:product')

    context = {'form': form, 'title': 'Create a New Product'}
    return render(request, 'sales/product-form.html', context)


# Update product
@login_required(login_url='sales:login')
def product_update(request, product_id):
    product = Product.objects.get(pk=product_id)
    form = ProductForm(instance=product)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            product_name = request.POST.get('name')
            messages.success(request, 'Successfully updated product:  ' + product_name)
            return redirect('sales:product')

    context = {'form': form, 'title': 'Update Product Information'}
    return render(request, 'sales/product-form.html', context)


# Delete product
@login_required(login_url='sales:login')
def product_delete(request, product_id):
    product = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        product.delete()
        messages.warning(request, str(product) + ' has been deleted.')
        return redirect('sales:product')
    context = {'product': product}
    return render(request, 'sales/product-delete.html', context)


# Create order
@login_required(login_url='sales:login')
def order_create(request, pk):
    customer = Customer.objects.get(pk=pk)

    if request.user.profile.id == customer.user_profile.id:
        OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'quantity', 'status'), max_num=3, can_delete=False)
        formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)

        if request.method == 'POST':
            formset = OrderFormSet(request.POST, instance=customer)
            if formset.is_valid():
                formset.save()

                # Update product inventory
                for form in formset:
                    ordered_product = form.cleaned_data.get('product')
                    ordered_quantity = form.cleaned_data.get('quantity')
                    product = Product.objects.filter(name=ordered_product).first()
                    if product is not None:
                        product.inventory -= ordered_quantity
                        product.save()
                messages.success(request, 'Successfully created order.')
                return HttpResponseRedirect(reverse('sales:detail', kwargs={'pk': customer.id}))

        context = {'formset': formset, 'title': 'Create New Orders'}
        return render(request, 'sales/order-form.html', context)
    else:
        messages.info(request, 'You are not authorized to view this page...')
        return redirect('sales:index')


# Update order
@login_required(login_url='sales:login')
def order_update(request, pk, order_id):
    customer = get_object_or_404(Customer, pk=pk)
    order = Order.objects.get(pk=order_id)

    if request.user.profile.id == customer.user_profile.id:
        form = OrderForm(instance=order)

        if request.method == 'POST':
            form = OrderForm(request.POST, instance=order)

            if form.is_valid():
                form.save()
                messages.success(request, 'Successfully updated order!')
                return HttpResponseRedirect(reverse('sales:detail', kwargs={'pk': customer.id}))

        context = {'form': form, 'title': 'Update Order Information'}
        return render(request, 'sales/order-form.html', context)
    else:
        messages.info(request, 'You are not authorized to view this page...')
        return redirect('sales:index')


# Delete order
@login_required(login_url='sales:login')
def order_delete(request, pk, order_id):
    customer = get_object_or_404(Customer, pk=pk)
    order = Order.objects.get(pk=order_id)

    if request.user.profile.id == customer.user_profile.id:
        if request.method == 'POST':
            order.delete()

            # Update product inventory
            product = order.product
            quantity = order.quantity
            product = Product.objects.filter(name=product).first()
            if product is not None:
                product.inventory += quantity
                product.save()
            messages.warning(request, 'Order:  ' + str(product) + ' - ' + str(quantity) + ' has been deleted.')
            return HttpResponseRedirect(reverse('sales:detail', kwargs={'pk': customer.id}))

        context = {'order': order, 'customer': customer}
        return render(request, 'sales/order-delete.html', context)
    else:
        messages.info(request, 'You are not authorized to view this page...')
        return redirect('sales:index')
