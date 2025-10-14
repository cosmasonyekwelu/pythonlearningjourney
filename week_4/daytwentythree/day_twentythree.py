"""
Day 23 - Django Setup & ORM Mastery
Date: October 14, 2025
"""

import os
import sys
import django
from datetime import datetime, timedelta


def django_fundamentals_summary():
    """
    SUMMARY OF DJANGO CONCEPTS FROM ALL LEARNING RESOURCES
    """

    print("=" * 70)
    print("🎯 DAY 23 - DJANGO SETUP & ORM MASTERY")
    print("=" * 70)

    concepts = {
        "django_architecture": {
            "title": "🚀 Django Architecture & Philosophy",
            "points": [
                "MVT Pattern (Model-View-Template) - Django's version of MVC",
                "Batteries-Included: Comes with admin, auth, ORM, templates built-in",
                "Don't Repeat Yourself (DRY) principle throughout framework",
                "Explicit is better than implicit - clear configuration over magic"
            ],
            "resources": ["Django Girls", "Official Docs"]
        },

        "project_structure": {
            "title": "📁 Project vs App Structure",
            "points": [
                "Project: Complete web application (trading_journal/)",
                "App: Web application component (trades/, users/, blog/)",
                "manage.py: Django command-line utility",
                "settings.py: Project configuration and settings",
                "urls.py: URL declarations (URLconf)",
                "__init__.py: Python package marker"
            ],
            "resources": ["Django Girls", "W3Schools"]
        },

        "models_orm": {
            "title": "🗄️ Models & Django ORM",
            "points": [
                "Models are Python classes that represent database tables",
                "Each model maps to a single database table",
                "Fields define the database columns and data types",
                "ORM (Object-Relational Mapping) converts Python to SQL",
                "Automatic primary key (id) if not specified",
                "Model methods represent business logic"
            ],
            "resources": ["Official Docs", "GeeksforGeeks"]
        },

        "migrations": {
            "title": "🔄 Database Migrations",
            "points": [
                "Migrations are Django's way of propagating database schema changes",
                "makemigrations - creates new migrations based on model changes",
                "migrate - applies migrations to database",
                "Migration files are version control for your database schema",
                "Never edit migration files manually!"
            ],
            "resources": ["Official Docs", "Django Girls"]
        },

        "admin_interface": {
            "title": "⚙️ Django Admin Interface",
            "points": [
                "Automatic admin interface for model management",
                "Built-in authentication and permissions",
                "Customizable list displays, filters, and search",
                "Model registration required: admin.site.register(Model)",
                "Admin classes for customization (list_display, list_filter)"
            ],
            "resources": ["Django Girls", "W3Schools"]
        },

        "views_urls": {
            "title": "🔗 Views & URL Configuration",
            "points": [
                "Views: Python functions/classes that receive web requests, return responses",
                "URLconf: Maps URL patterns to views",
                "Function-based views (FBV) vs Class-based views (CBV)",
                "URL patterns use regular expressions or path converters",
                "Reverse URL lookups with {% url %} template tag and reverse() function"
            ],
            "resources": ["Official Docs", "GeeksforGeeks"]
        },

        "templates": {
            "title": "🎨 Django Template Language",
            "points": [
                "Template inheritance with {% extends %} and {% block %}",
                "Variable output with {{ variable }}",
                "Template tags for logic: {% for %}, {% if %}, {% url %}",
                "Filters for data transformation: {{ value|lower }}",
                "Automatic HTML escaping for security"
            ],
            "resources": ["Django Girls", "W3Schools"]
        },

        "querysets": {
            "title": "📊 QuerySets & Database Operations",
            "points": [
                "QuerySets are lazy - not executed until evaluated",
                "Chaining filters: Model.objects.filter().exclude().order_by()",
                "Field lookups: Model.objects.filter(price__gt=100)",
                "Aggregations: .count(), .aggregate(), .annotate()",
                "Related objects: select_related() and prefetch_related() for performance"
            ],
            "resources": ["Official Docs", "GeeksforGeeks"]
        }
    }

    for key, concept in concepts.items():
        print(f"\n{concept['title']}")
        print("-" * 50)
        for point in concept['points']:
            print(f"  • {point}")
        print(f"  📚 Resources: {', '.join(concept['resources'])}")

    return concepts


def practical_code_examples():
    """
    PRACTICAL CODE EXAMPLES FROM LEARNING RESOURCES
    """

    print("\n" + "=" * 70)
    print("💻 PRACTICAL CODE EXAMPLES")
    print("=" * 70)

    examples = {
        "project_setup": {
            "title": "1. Project & App Setup Commands",
            "code": """
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install Django
pip install Django

# Create project
django-admin startproject trading_journal .

# Create app
python manage.py startapp trades

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
            """,
            "explanation": "Basic Django project setup sequence"
        },

        "model_definition": {
            "title": "2. Model Definition (trades/models.py)",
            "code": """
from django.db import models
from django.urls import reverse

class Trade(models.Model):
    SYMBOL_CHOICES = [
        ('AAPL', 'Apple Inc.'),
        ('GOOGL', 'Alphabet Inc.'),
        ('MSFT', 'Microsoft'),
        ('TSLA', 'Tesla Inc.'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open Position'),
        ('CLOSED', 'Closed Position'),
        ('PENDING', 'Pending Execution'),
    ]
    
    # Database fields
    symbol = models.CharField(max_length=10, choices=SYMBOL_CHOICES)
    trade_type = models.CharField(max_length=4, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
    quantity = models.PositiveIntegerField()
    entry_price = models.DecimalField(max_digits=10, decimal_places=2)
    exit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entry_date = models.DateTimeField(auto_now_add=True)
    exit_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    notes = models.TextField(blank=True)
    
    # Metadata
    class Meta:
        ordering = ['-entry_date']  # Default ordering
        verbose_name_plural = "Trades"  # Admin display name
    
    # String representation
    def __str__(self):
        return f"{self.symbol} {self.trade_type} - {self.quantity} shares"
    
    # Absolute URL for detail view
    def get_absolute_url(self):
        return reverse('trade_detail', kwargs={'pk': self.pk})
    
    # Custom property (not in database)
    @property
    def current_value(self):
        return self.quantity * self.entry_price
    
    @property
    def profit_loss(self):
        if self.exit_price and self.trade_type == 'BUY':
            return (self.exit_price - self.entry_price) * self.quantity
        return None
            """,
            "explanation": "Complete model with fields, choices, methods, and properties"
        },

        "admin_configuration": {
            "title": "3. Admin Configuration (trades/admin.py)",
            "code": """
from django.contrib import admin
from .models import Trade

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    # List display configuration
    list_display = ['symbol', 'trade_type', 'quantity', 'entry_price', 'status', 'entry_date']
    list_filter = ['symbol', 'trade_type', 'status', 'entry_date']
    search_fields = ['symbol', 'notes']
    readonly_fields = ['entry_date']
    
    # Fieldsets for organized form display
    fieldsets = (
        ('Trade Information', {
            'fields': ('symbol', 'trade_type', 'quantity', 'entry_price')
        }),
        ('Exit Information', {
            'fields': ('exit_price', 'exit_date', 'status'),
            'classes': ('collapse',)  # Collapsible section
        }),
        ('Additional Info', {
            'fields': ('notes',)
        }),
    )
    
    # Actions for bulk operations
    actions = ['mark_as_closed']
    
    def mark_as_closed(self, request, queryset):
        queryset.update(status='CLOSED')
    mark_as_closed.short_description = "Mark selected trades as closed"
            """,
            "explanation": "Custom admin interface with list display, filters, and actions"
        },

        "views_implementation": {
            "title": "4. Views Implementation (trades/views.py)",
            "code": """
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q  # For complex queries
from .models import Trade

# Class-Based Views (Recommended)
class TradeListView(ListView):
    model = Trade
    template_name = 'trades/trade_list.html'
    context_object_name = 'trades'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtering based on URL parameters
        symbol = self.request.GET.get('symbol')
        status = self.request.GET.get('status')
        
        if symbol:
            queryset = queryset.filter(symbol__icontains=symbol)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add extra context
        context['total_trades'] = Trade.objects.count()
        context['open_trades'] = Trade.objects.filter(status='OPEN').count()
        return context

class TradeDetailView(DetailView):
    model = Trade
    template_name = 'trades/trade_detail.html'

class TradeCreateView(CreateView):
    model = Trade
    fields = ['symbol', 'trade_type', 'quantity', 'entry_price', 'notes']
    template_name = 'trades/trade_form.html'
    success_url = reverse_lazy('trade_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Trade created successfully!')
        return super().form_valid(form)

# Function-Based View Example
def trade_dashboard(request):
    \"\"\"Custom dashboard view\"\"\"
    trades = Trade.objects.all()
    
    # Complex query with Q objects
    recent_trades = trades.filter(
        Q(status='OPEN') | Q(entry_date__gte=datetime.now() - timedelta(days=7))
    )
    
    context = {
        'total_trades': trades.count(),
        'open_trades': trades.filter(status='OPEN').count(),
        'recent_trades': recent_trades,
        'portfolio_value': sum(trade.current_value for trade in trades.filter(status='OPEN'))
    }
    
    return render(request, 'trades/dashboard.html', context)
            """,
            "explanation": "Both class-based and function-based views with filtering and context"
        },

        "url_configuration": {
            "title": "5. URL Configuration (trades/urls.py)",
            "code": """
from django.urls import path
from . import views

app_name = 'trades'  # Namespace for URL reversing

urlpatterns = [
    # Class-based views
    path('', views.TradeListView.as_view(), name='trade_list'),
    path('trade/<int:pk>/', views.TradeDetailView.as_view(), name='trade_detail'),
    path('trade/new/', views.TradeCreateView.as_view(), name='trade_create'),
    path('trade/<int:pk>/edit/', views.TradeUpdateView.as_view(), name='trade_update'),
    path('trade/<int:pk>/delete/', views.TradeDeleteView.as_view(), name='trade_delete'),
    
    # Function-based views
    path('dashboard/', views.trade_dashboard, name='dashboard'),
    
    # API endpoints
    path('api/trades/', views.trade_list_api, name='trade_list_api'),
]

# Project-level URLs (trading_journal/urls.py)
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('trades/', include('trades.urls')),  # Include app URLs
    path('', RedirectView.as_view(pattern_name='trades:trade_list')),  # Home redirect
]
            """,
            "explanation": "URL configuration with namespacing and include patterns"
        },

        "template_examples": {
            "title": "6. Template Examples (templates/)",
            "code": """
<!-- base.html - Template Inheritance -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Trading Journal{% endblock %}</title>
</head>
<body>
    <nav>...</nav>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
</body>
</html>

<!-- trade_list.html -->
{% extends "base.html" %}

{% block title %}All Trades{% endblock %}

{% block content %}
<h1>Trading Records</h1>

<!-- Template Filters -->
<p>Total Trades: {{ trades.count }}</p>
<p>Last Updated: {{ current_time|date:"F j, Y" }}</p>

<!-- For Loop -->
<table>
{% for trade in trades %}
    <tr>
        <td>{{ trade.symbol }}</td>
        <td>{{ trade.quantity }}</td>
        <td>${{ trade.entry_price }}</td>
        <!-- Conditional -->
        <td class="{% if trade.profit_loss > 0 %}profit{% else %}loss{% endif %}">
            ${{ trade.profit_loss|default:"0.00" }}
        </td>
        <!-- URL reversing -->
        <td><a href="{% url 'trades:trade_detail' trade.pk %}">View</a></td>
    </tr>
{% empty %}
    <tr><td colspan="5">No trades found.</td></tr>
{% endfor %}
</table>

<!-- Pagination -->
{% if is_paginated %}
    <div class="pagination">
        Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}
    </div>
{% endif %}
{% endblock %}
            """,
            "explanation": "Template inheritance, filters, loops, conditionals, and URL reversing"
        },

        "queryset_examples": {
            "title": "7. QuerySet Examples (Database Operations)",
            "code": """
# Basic queries
all_trades = Trade.objects.all()
open_trades = Trade.objects.filter(status='OPEN')
single_trade = Trade.objects.get(pk=1)  # Raises exception if not found

# Field lookups
expensive_trades = Trade.objects.filter(entry_price__gt=100)
recent_trades = Trade.objects.filter(entry_date__gte=datetime.now() - timedelta(days=30))
apple_trades = Trade.objects.filter(symbol__icontains='AAPL')

# Chaining queries
profitable_trades = (Trade.objects
    .filter(status='CLOSED')
    .exclude(exit_price__lte=models.F('entry_price'))
    .order_by('-entry_date')
)

# Aggregations
from django.db.models import Count, Sum, Avg
trade_stats = Trade.objects.aggregate(
    total_trades=Count('id'),
    total_volume=Sum('quantity'),
    avg_price=Avg('entry_price')
)

# Annotations (adding computed values to each object)
from django.db.models import F, ExpressionWrapper, DecimalField
trades_with_value = Trade.objects.annotate(
    total_value=ExpressionWrapper(
        F('quantity') * F('entry_price'),
        output_field=DecimalField()
    )
)

# Related objects optimization
trades_with_portfolio = Trade.objects.select_related('portfolio').all()

# Bulk operations
Trade.objects.filter(status='OPEN').update(status='CLOSED')
            """,
            "explanation": "Various QuerySet operations including filtering, aggregation, and optimization"
        }
    }

    for key, example in examples.items():
        print(f"\n{example['title']}")
        print("-" * 50)
        print(example['code'])
        print(f"💡 {example['explanation']}")
        print()


def django_workflow_demonstration():
    """
    COMPLETE DJANGO DEVELOPMENT WORKFLOW
    """

    print("\n" + "=" * 70)
    print("🔄 DJANGO DEVELOPMENT WORKFLOW")
    print("=" * 70)

    workflow = [
        ("1. Project Planning", "Define models and relationships"),
        ("2. Create Project", "django-admin startproject myproject"),
        ("3. Create Apps", "python manage.py startapp myapp"),
        ("4. Define Models", "Create models in models.py"),
        ("5. Create Migrations", "python manage.py makemigrations"),
        ("6. Apply Migrations", "python manage.py migrate"),
        ("7. Create Admin", "python manage.py createsuperuser"),
        ("8. Register Models", "Add models to admin.py"),
        ("9. Create Views", "Implement views in views.py"),
        ("10. Configure URLs", "Set up URL patterns in urls.py"),
        ("11. Create Templates", "Build HTML templates"),
        ("12. Test & Debug", "Run server and test functionality"),
        ("13. Add Static Files", "CSS, JavaScript, images"),
        ("14. Deploy", "Prepare for production")
    ]

    for step, description in workflow:
        print(f"{step:25} {description}")


def key_learnings_cheatsheet():
    """
    ESSENTIAL DJANGO CONCEPTS CHEATSHEET
    """

    print("\n" + "=" * 70)
    print("📋 DJANGO ESSENTIALS CHEATSHEET")
    print("=" * 70)

    cheatsheet = {
        "Commands": [
            "django-admin startproject projectname",
            "python manage.py startapp appname",
            "python manage.py makemigrations",
            "python manage.py migrate",
            "python manage.py createsuperuser",
            "python manage.py runserver",
            "python manage.py shell"
        ],

        "Model Fields": [
            "CharField, TextField, IntegerField, DecimalField",
            "DateTimeField, DateField, TimeField",
            "BooleanField, EmailField, URLField",
            "ForeignKey, ManyToManyField, OneToOneField",
            "FileField, ImageField"
        ],

        "Common Field Options": [
            "null=True/False (database NULL)",
            "blank=True/False (form validation)",
            "default=value (default value)",
            "choices=LIST (dropdown options)",
            "verbose_name='Human readable'",
            "help_text='Help text for forms'"
        ],

        "QuerySet Methods": [
            ".all(), .get(), .filter(), .exclude()",
            ".order_by(), .reverse(), .distinct()",
            ".values(), .values_list()",
            ".count(), .exists(), .first(), .last()",
            ".aggregate(), .annotate()",
            ".select_related(), .prefetch_related()"
        ],

        "Field Lookups": [
            "exact, iexact (case-insensitive exact)",
            "contains, icontains",
            "in, gt, gte, lt, lte",
            "startswith, istartswith, endswith, iendswith",
            "range, date, year, month, day",
            "isnull"
        ],

        "Template Tags": [
            "{% for %} {% endfor %}",
            "{% if %} {% elif %} {% else %} {% endif %}",
            "{% block %} {% endblock %}",
            "{% extends 'base.html' %}",
            "{% include 'partial.html' %}",
            "{% url 'view_name' %}",
            "{% csrf_token %}"
        ],

        "Template Filters": [
            "{{ value|length }}",
            "{{ value|lower }} {{ value|upper }}",
            "{{ value|title }} {{ value|capfirst }}",
            "{{ value|date:'Y-m-d' }}",
            "{{ value|default:'N/A' }}",
            "{{ value|truncatewords:50 }}",
            "{{ value|floatformat:2 }}"
        ]
    }

    for category, items in cheatsheet.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")


def main():
    """
    MAIN EXECUTION - RUNS ALL LEARNING SECTIONS
    """
    print("🎓 DAY 23 - DJANGO SETUP & ORM COMPLETE LEARNING PACKAGE")
    print("Based on: Django Girls, Official Docs, W3Schools, GeeksforGeeks")
    print("=" * 70)

    # Run all learning sections
    django_fundamentals_summary()
    practical_code_examples()
    django_workflow_demonstration()
    key_learnings_cheatsheet()

    print("\n" + "=" * 70)
    print("✅ LEARNING COMPLETE!")
    print("Next: Apply these concepts in your Django trading journal project")
    print("=" * 70)


if __name__ == "__main__":
    main()
