from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView

from webapp.forms import CartAddForm, OrderForm
from webapp.models import Cart, Product, Order, OrderProduct


class CartView(ListView):
    template_name = 'order/cart_view.html'
    context_object_name = 'cart'

    def get_queryset(self):
        return Cart.get_with_product()

    def get_context_data(self, *, object_list=None, **kwargs):
        if not self.request.session.session_key:
            self.request.session.save()
        session = Session.objects.get(session_key=self.request.session.session_key)
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['cart_total'] = Cart.get_cart_total(session=session)
        context['form'] = OrderForm()
        context['cart'] = context['cart'].filter(session=session)
        return context


class CartAddView(CreateView):
    model = Cart
    form_class = CartAddForm

    def post(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=self.kwargs.get('pk'))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        qty = form.cleaned_data.get('qty', 1)
        if not self.request.session.session_key:
            self.request.session.save()
        session = Session.objects.get(session_key=self.request.session.session_key)
        try:
            cart_product = Cart.objects.get(product=self.product, session=session)
            cart_product.qty += qty
            if cart_product.qty <= self.product.amount:
                cart_product.save()
        except Cart.DoesNotExist:
            if qty <= self.product.amount:
                Cart.objects.create(product=self.product, qty=qty, session=session)
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        return redirect(self.get_success_url())

    def get_success_url(self):
        next = self.request.GET.get('next')
        if next:
            return next
        return reverse('webapp:index')


class CartDeleteView(DeleteView):
    model = Cart
    success_url = reverse_lazy('webapp:cart_view')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class CartDeleteOneView(DeleteView):
    model = Cart
    success_url = reverse_lazy('webapp:cart_view')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        self.object.qty -= 1
        if self.object.qty < 1:
            self.object.delete()
        else:
            self.object.save()

        return redirect(success_url)


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('webapp:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        order = self.object
        try:
            order.user = self.request.user
        except ValueError:
            order.user = None
        order.save()
        session = Session.objects.get(session_key=self.request.session.session_key)
        cart_products = Cart.objects.filter(session=session)
        products = []
        order_products = []

        for item in cart_products:
            if item.product.amount >= item.qty:
                product = item.product
                qty = item.qty
                product.amount -= qty
                products.append(product)
                order_product = OrderProduct(order=order, product=product, qty=qty)
                order_products.append(order_product)
        OrderProduct.objects.bulk_create(order_products)
        Product.objects.bulk_update(products, ('amount',))
        cart_products.delete()
        return response

    def form_invalid(self, form):
        return redirect('webapp:cart_view')


class WatchOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/orders_View.html'
    context_object_name = 'orders'

    def get_queryset(self):
        data = super().get_queryset()
        data = data.filter(user=self.request.user)
        return data
