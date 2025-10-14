# Django Quick Reference Cheatsheet

## 🏗️ Project Structure
```
project/
├── manage.py                 # Django command-line utility
├── project/                  # Project package
│   ├── __init__.py
│   ├── settings.py          # Project settings & configuration
│   ├── urls.py              # Project URL declarations
│   └── wsgi.py              # WSGI web server interface
└── app/                     # Application package
    ├── migrations/          # Database migration files
    ├── __init__.py
    ├── admin.py             # Admin interface configuration
    ├── apps.py              # Application configuration
    ├── models.py            # Database models
    ├── tests.py             # Test cases
    ├── views.py             # View functions/classes
    └── urls.py              # Application URL routing
```

## 🚀 Common Commands

### Project Management
```bash
# Create new project
django-admin startproject myproject

# Create new app
python manage.py startapp myapp

# Run development server
python manage.py runserver
python manage.py runserver 8080          # Specific port
python manage.py runserver 0.0.0.0:8000  # External access
```

### Database Operations
```bash
# Create migrations from model changes
python manage.py makemigrations
python manage.py makemigrations appname  # Specific app

# Apply migrations to database
python manage.py migrate
python manage.py migrate appname         # Specific app
python manage.py migrate appname 0001    # Specific migration

# Show migration status
python manage.py showmigrations

# Create admin user
python manage.py createsuperuser
```

### Development Utilities
```bash
# Django shell (with models loaded)
python manage.py shell

# Run tests
python manage.py test
python manage.py test appname

# Collect static files for production
python manage.py collectstatic

# Check project for common issues
python manage.py check
```

## 📊 Model Field Types

### Basic Fields
```python
from django.db import models

class MyModel(models.Model):
    # Text Fields
    name = models.CharField(max_length=100)           # Short text
    description = models.TextField()                  # Long text
    slug = models.SlugField()                         # URL-friendly text
    
    # Numeric Fields
    age = models.IntegerField()                       # Whole numbers
    price = models.DecimalField(max_digits=10, decimal_places=2)
    percentage = models.FloatField()                  # Floating point
    balance = models.PositiveIntegerField()           # Positive only
    
    # Date/Time Fields
    created = models.DateTimeField(auto_now_add=True) # Set on create
    updated = models.DateTimeField(auto_now=True)     # Set on save
    birthday = models.DateField()                     # Date only
    time = models.TimeField()                         # Time only
    
    # Boolean Fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Specialized Fields
    email = models.EmailField()                       # Email validation
    website = models.URLField()                       # URL validation
    photo = models.ImageField(upload_to='photos/')    # Image files
    document = models.FileField(upload_to='docs/')    # Any files
    json_data = models.JSONField()                    # JSON data
```

### Relationship Fields
```python
class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    title = models.CharField(max_length=200)
    # One-to-Many: Book has one author, Author has many books
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    
    # Many-to-Many: Book can have multiple categories
    categories = models.ManyToManyField('Category')
    
    # One-to-One: Each book has one unique detail record
    details = models.OneToOneField('BookDetails', on_delete=models.CASCADE)

class Category(models.Model):
    name = models.CharField(max_length=50)

class BookDetails(models.Model):
    summary = models.TextField()
```

## ⚙️ Common Field Options

```python
class Product(models.Model):
    # Required vs Optional
    name = models.CharField(max_length=100)                    # Required
    description = models.TextField(blank=True)                 # Optional in forms
    sku = models.CharField(max_length=50, null=True)          # Optional in DB
    
    # Default Values
    is_available = models.BooleanField(default=True)
    priority = models.IntegerField(default=1)
    
    # Choices (Dropdown)
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    
    # Help Text & Labels
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Retail Price",
        help_text="Price in USD"
    )
    
    # Database Indexing
    code = models.CharField(max_length=20, db_index=True)     # Single field index
    
    class Meta:
        indexes = [
            models.Index(fields=['name', 'status']),          # Composite index
        ]
        ordering = ['-created']                               # Default ordering
```

## 🔍 QuerySet Operations

### Basic Retrieval
```python
# Get all objects
all_objects = MyModel.objects.all()

# Get single object (raises exception if not found)
obj = MyModel.objects.get(pk=1)
obj = MyModel.objects.get(name="Example")

# Get single object or None
obj = MyModel.objects.filter(pk=1).first()

# Check existence
exists = MyModel.objects.filter(name="Example").exists()

# Count objects
count = MyModel.objects.count()
```

### Filtering & Excluding
```python
# Basic filtering
active_users = User.objects.filter(is_active=True)
inactive_users = User.objects.exclude(is_active=True)

# Multiple conditions
users = User.objects.filter(is_active=True, is_staff=False)

# OR conditions with Q objects
from django.db.models import Q
users = User.objects.filter(Q(is_active=True) | Q(is_staff=True))

# Field lookups
products = Product.objects.filter(price__gt=100)           # Greater than
products = Product.objects.filter(price__gte=50)           # Greater than or equal
products = Product.objects.filter(price__lt=200)           # Less than
products = Product.objects.filter(name__contains='pro')    # Contains
products = Product.objects.filter(name__icontains='pro')   # Case-insensitive contains
products = Product.objects.filter(name__startswith='A')    # Starts with
products = Product.objects.filter(name__endswith='z')      # Ends with
products = Product.objects.filter(name__in=['A', 'B', 'C']) # In list
products = Product.objects.filter(created__year=2024)      # Date lookups
```

### Sorting & Limiting
```python
# Ordering
products = Product.objects.order_by('name')                # Ascending
products = Product.objects.order_by('-price')              # Descending
products = Product.objects.order_by('category', '-price')  # Multiple fields

# Slicing
first_10 = Product.objects.all()[:10]                      # First 10
next_10 = Product.objects.all()[10:20]                     # Next 10

# Distinct values
categories = Product.objects.values_list('category', flat=True).distinct()
```

### Aggregation & Annotation
```python
from django.db.models import Count, Sum, Avg, Max, Min

# Aggregation (returns dict)
stats = Product.objects.aggregate(
    total=Count('id'),
    total_value=Sum('price'),
    avg_price=Avg('price'),
    max_price=Max('price'),
    min_price=Min('price')
)

# Annotation (adds field to each object)
from django.db.models import F, ExpressionWrapper, DecimalField
products = Product.objects.annotate(
    discounted_price=ExpressionWrapper(
        F('price') * 0.9,
        output_field=DecimalField()
    )
)

# Group by with annotation
categories = Product.objects.values('category').annotate(
    product_count=Count('id'),
    avg_price=Avg('price')
)
```

### Performance Optimization
```python
# select_related (Foreign Key - One-to-One)
books = Book.objects.select_related('author')              # Single SQL query

# prefetch_related (Many-to-Many, Reverse Foreign Key)
books = Book.objects.prefetch_related('categories')        # Additional query

# Combined
books = Book.objects.select_related('author').prefetch_related('categories')

# Only/defer for partial field loading
books = Book.objects.only('title', 'author__name')         # Load only these
books = Book.objects.defer('description')                  # Load all except
```

## 🎨 Template System

### Basic Syntax
```django
<!-- Variables -->
<p>Hello, {{ user.username }}!</p>
<p>Price: ${{ product.price }}</p>

<!-- Filters -->
<p>{{ name|lower }}</p>
<p>{{ bio|truncatewords:30 }}</p>
<p>{{ created_date|date:"F j, Y" }}</p>
<p>{{ value|default:"N/A" }}</p>
<p>{{ list|length }}</p>
<p>{{ text|linebreaks }}</p>

<!-- Tags -->
{% if user.is_authenticated %}
    <p>Welcome back!</p>
{% else %}
    <p>Please log in.</p>
{% endif %}

{% for item in items %}
    <p>{{ forloop.counter }}. {{ item.name }}</p>
{% empty %}
    <p>No items found.</p>
{% endfor %}

{% with total=items|length %}
    <p>Total: {{ total }}</p>
{% endwith %}
```

### Template Inheritance
```django
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    <nav>{% include "_navigation.html" %}</nav>
    <main>{% block content %}{% endblock %}</main>
    <footer>{% include "_footer.html" %}</footer>
</body>
</html>

<!-- child.html -->
{% extends "base.html" %}

{% block title %}My Page - My Site{% endblock %}

{% block content %}
<h1>Welcome to my page</h1>
<p>This content goes in the main block.</p>
{% endblock %}
```

### URL Handling in Templates
```django
<!-- Basic URL -->
<a href="{% url 'home' %}">Home</a>

<!-- URL with parameters -->
<a href="{% url 'product_detail' product.id %}">{{ product.name }}</a>

<!-- URL with keyword arguments -->
<a href="{% url 'profile' username=user.username %}">Profile</a>

<!-- Static files -->
{% load static %}
<img src="{% static 'images/logo.png' %}" alt="Logo">
<link href="{% static 'css/style.css' %}" rel="stylesheet">
```

## 🎯 Class-Based Views

### Common Generic Views
```python
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'  # Default: object_list
    paginate_by = 20
    
    def get_queryset(self):
        # Custom queryset
        return Product.objects.filter(is_active=True).order_by('-created')

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'

class ProductCreateView(CreateView):
    model = Product
    fields = ['name', 'description', 'price', 'category']
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')
    
    def form_valid(self, form):
        # Custom logic before saving
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'description', 'price', 'category']
    template_name = 'products/product_form.html'

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')
```

### Function-Based Views
```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})
```

## 🔗 URL Configuration

### Project URLs
```python
# project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path('blog/', include('blog.urls')),
    path('', RedirectView.as_view(pattern_name='home'), name='home'),
]
```

### App URLs
```python
# products/urls.py
from django.urls import path
from . import views

app_name = 'products'  # Namespace

urlpatterns = [
    # Function-based views
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    
    # Class-based views
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # API endpoints
    path('api/', views.product_api_list, name='product_api_list'),
]
```

### URL Patterns
```python
# Basic patterns
path('about/', views.about, name='about'),

# Path converters
path('user/<int:user_id>/', views.user_profile, name='user_profile'),
path('post/<slug:slug>/', views.post_detail, name='post_detail'),
path('category/<str:category_name>/', views.category_view, name='category'),
path('path/<path:subpath>/', views.path_view, name='path_view'),

# Regular expressions (re_path)
from django.urls import re_path
re_path(r'^articles/(?P<year>[0-9]{4})/$', views.year_archive, name='year_archive'),
```

## ⚙️ Admin Interface

### Basic Registration
```python
from django.contrib import admin
from .models import Product, Category

# Simple registration
admin.site.register(Product)
admin.site.register(Category)

# Custom admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'is_active', 'created']
    list_filter = ['category', 'is_active', 'created']
    search_fields = ['name', 'description']
    readonly_fields = ['created', 'updated']
    list_editable = ['price', 'is_active']
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_active', 'created', 'updated')
        }),
    )
    
    # Custom methods
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')
```

### Admin Actions
```python
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Custom admin actions
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} products activated.')
    make_active.short_description = "Activate selected products"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} products deactivated.')
    make_inactive.short_description = "Deactivate selected products"
```

## 🔧 Settings Configuration

### Essential Settings
```python
# settings.py

# Security
DEBUG = True  # False in production!
SECRET_KEY = 'your-secret-key-here'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'yourdomain.com']

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    
    # Local apps
    'products',
    'users',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# For PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'mydatabaseuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
```

## 🛡️ Security & Best Practices

### Security Middleware
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### CSRF Protection
```django
<!-- In templates -->
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

```python
# In views (for AJAX)
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Use carefully!
def my_api_view(request):
    # Handle request
    pass
```

### Authentication
```python
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def protected_view(request):
    pass

@permission_required('app.change_model')
def staff_view(request):
    pass

# In class-based views
from django.contrib.auth.mixins import LoginRequiredMixin

class ProtectedView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
```

## 📝 Common Patterns

### get_object_or_404 Pattern
```python
from django.shortcuts import get_object_or_404

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Instead of Product.objects.get(pk=pk) which raises 500 error
    return render(request, 'product_detail.html', {'product': product})
```

### Success Messages
```python
from django.contrib import messages

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'form.html', {'form': form})
```

### Form Handling
```python
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError("Price cannot be negative")
        return price
```

This cheatsheet covers the most essential Django concepts and patterns 