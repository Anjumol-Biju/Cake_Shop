
import razorpay

from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView,DetailView
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from cakeshop.forms import RegistrationForm,LoginForm
from cakeshop.models import Cake,CakeVariant,BasketItem,Occasion,Flavour,Basket,Order,OrderItems,Category
from cakeshop.decorators import signin_required,owner_permission_required


KEY_ID="rzp_test_yxxG5GBkjlIPmA"    
KEY_SECRET="X28toQnvQjjkfFZtgVkc2ao0"



# Create your views here.

def signin_required(fn):
    def wrapper(request,*args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request,"invalid session")
            return redirect("signin")
        else:
            return fn(request,*args, **kwargs)
    return wrapper


# url:localhost:8000/register/
# method: get,post
# form_class:registrationform


class SignUpView(View):
    def get(self,request,*args,**kwargs):
        form=RegistrationForm()
        return render(request,"register.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("signin")
        return render(request,"login.html",{"form":form})
    


# url:localhost:8000/
# method: get,post
# form_class:LoginForm
class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"login.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            u_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=u_name,password=pwd)
            if user_object:
                login(request,user_object)
                return redirect("index")
        messages.error(request,"Invalid Credentials")
        return render(request,"login.html",{"form":form})

# class IndexView(TemplateView):

#     template_name="index.html"

@method_decorator([signin_required,never_cache],name="dispatch")
class IndexView(View):
    def get(self,request,*args,**kwargs):
        qs=Cake.objects.all()
        
        categories=Category.objects.all()
        
        print(request.GET)
        
        selected_category=request.GET.get("category")
        if selected_category:
            qs=qs.filter(category_object__name=selected_category)
        
       
        return render(request,"index.html",{"data":qs,"categories":categories})
    
    
# class CakeDetailView(View):
    
#     def get(self,request,*args,**kwargs):
#         id=kwargs.get("pk")
#         qs=Cake.objects.get(id=id)
#         return render(request,"cake_detail.html",{"data":qs})
    
    
# class CakeDetailView(View):
#     def get(self,request,*args,**kwargs):
#         cake_id = kwargs.get("pk")
#         cake_object=Cake.objects.get(id=cake_id)
#         qs=CakeVariant.objects.filter(cake_object=cake_id)
#         print(qs)

# class CakeDetailView(DetailView):
#     template_name="cake_detail.html"
#     model=Cake
#     context_object_name="data"
@method_decorator([signin_required,never_cache],name="dispatch")
class CakeDetailView(View):
    def get(self, request, *args, **kwargs):
        cake_id = kwargs.get("pk")
        cake_object=Cake.objects.get(id=cake_id)
        qs=CakeVariant.objects.filter(cake_object=cake_id)
        print(qs)
        return render(request, "cake_detail.html",{"data":qs,"cake":cake_object})
    
class HomeView(TemplateView):
    template_name="home.html"
    
# add to basket 
# url:localhost:8000/products/{id}/add_to_basket/ 
@method_decorator([signin_required,never_cache],name="dispatch")
class AddToBasketView(View):
    def post(self, request, *args, **kwargs):
        occasion=Occasion.objects.get(name=request.POST.get("occasion"))  
        flavour=Flavour.objects.get(name=request.POST.get("flavour"))  
        note=request.POST.get("note")
        qty=request.POST.get("qty")
        id=kwargs.get("pk")
        cake_obj=CakeVariant.objects.get(id=id)
        basket=Basket.objects.get(owner=request.user)
        BasketItem.objects.create(
            cakevarient_object=cake_obj,
            occasion_object=occasion,
            flavour_object=flavour,
            note=note,
            qty=qty,
            basket_object=basket
            
        )
        return redirect("index")
        

# basket item list view
# url:localhost:8000/baske
@method_decorator([signin_required,never_cache],name="dispatch")
class BasketItemListView(View):
    
    def get(self,request,*args,**kwargs):
        qs=request.user.cart.cartitem.filter(is_order_placed=False)
        return render(request,"cart_list.html",{"data":qs})
    
        
        
#Basket Item Remove
#localhost:8000/basket/{id}/remove/
@method_decorator([signin_required,owner_permission_required,never_cache],name="dispatch")
class BasketItemRemoveView(View):
    
    def get(self,request,*args, **kwargs):
        id=kwargs.get("pk")
        basket_item_object=BasketItem.objects.get(id=id)
        basket_item_object.delete()
        return redirect("basket-items")  

@method_decorator([signin_required,owner_permission_required,never_cache],name="dispatch")
class CartItemUpdateQuatityView(View):
    
    def post(self,request,*args, **kwargs):
        action=request.POST.get("counterButton")
        print(action)
        id=kwargs.get("pk")
        basket_item_object=BasketItem.objects.get(id=id)
        if action=="+":
            basket_item_object.qty+=1
            basket_item_object.save()
            
        else:
            basket_item_object.qty-=1
            basket_item_object.save()
            
        return redirect("basket-items")



@method_decorator([signin_required,never_cache],name="dispatch")
class CheckOutView(View):
    
    def get (self,request,*args,**kwargs):
        
        return render(request,"checkout.html")
    
    def post(self,request,*args,**kwargs):
        
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        address=request.POST.get("address")
        
        payment_method=request.POST.get("payment")
        
        
        # print(email,phone,address)
        # step 1 create an order instance
        order_obj=Order.objects.create(
            user_object=request.user,
            delivery_address=address,
            phone=phone,
            email=email,
            total=request.user.cart.basket_total,
            
            payment=payment_method,
        )
        # step 2 create order_item instance 
        try:
            basket_items=request.user.cart.cart_items
            for bi in basket_items:
                OrderItems.objects.create(
                    order_object=order_obj,
                    basket_item_object=bi
                    
                )
                bi.is_order_placed=True
                bi.save()
                print("test block-1")
        except:
            order_obj.delete()
            
        #  update basket_item_object is_order_placed(True)    
        finally:
            
            print("test block-2")
            
            print(payment_method)
            print(order_obj)
            
            if payment_method=="online" and order_obj:
                
                print("test block-3")
                
                client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))
                
                # total=int()
                amount=int(order_obj.get_order_total*100)


                data = { "amount": amount, "currency": "INR", "receipt": "order_rcptid_11" }
                payment = client.order.create(data=data)
                
                order_obj.order_id=payment.get("id")
                order_obj.save()
                # print("payment initiate",payment)
                
                context={
                                "key":KEY_ID,
                                "order_id":payment.get("id"),
                                "amount":payment.get("amount")
                        }
                return render(request,"payment.html",{"context":context})
            
            return redirect("index")
        
"""
client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))

data = { "amount": 500, "currency": "INR", "receipt": "order_rcptid_11" }
payment = client.order.create(data=data)
"""
        
        
@method_decorator([signin_required,never_cache],name="dispatch")
class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")
    

class OrderSummaryView(View):
    def get(self,request,*args,**kwargs):
        qs=Order.objects.filter(user_object=request.user).exclude(status="cancelled")
        return render(request,"order_summary.html",{"data":qs})
        
        
        


#localhost:8000/orders/item/{id}/remove/
class OrderItemRemoveView(View):
    def get(self,request,*args, **kwargs):
        id=kwargs.get("pk")
        OrderItems.objects.get(id=id).delete()
        return redirect("order-summary")
    
    
@method_decorator(csrf_exempt,name="dispatch")    
class PaymentVerificationView(View):
    
    def post(self,request,*args,**kwargs):
        print("===============================",request.POST)
        client = razorpay.Client(auth=(KEY_ID,KEY_SECRET))

        data=request.POST
        try:
            
             client.utility.verify_payment_signature(data)
             print(data)
             order_obj=Order.objects.get(order_id=data.get("razorpay_order_id"))
             order_obj.is_paid=True
             order_obj.save()
             print("transaction completed******************")
             
        except:
            print("transaction failed!!!!!!!!!!!!!!!!!!!!!")
            
        return render(request,"success.html")
      
        
        
        
        