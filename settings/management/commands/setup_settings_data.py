from django.core.management.base import BaseCommand
from settings.models import Country, DeliveryCompany, SystemSetting
from roles.models import Role
from users.models import User
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Set up initial settings data including countries, delivery companies, and default fees'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial settings data...')
        
        # Create countries
        countries_data = [
            {'name_en': 'United States', 'name_ar': 'الولايات المتحدة', 'code': 'USA', 'currency': 'USD', 'timezone': 'America/New_York'},
            {'name_en': 'United Arab Emirates', 'name_ar': 'الإمارات العربية المتحدة', 'code': 'UAE', 'currency': 'AED', 'timezone': 'Asia/Dubai'},
            {'name_en': 'Saudi Arabia', 'name_ar': 'المملكة العربية السعودية', 'code': 'KSA', 'currency': 'SAR', 'timezone': 'Asia/Riyadh'},
            {'name_en': 'Egypt', 'name_ar': 'مصر', 'code': 'EGY', 'currency': 'EGP', 'timezone': 'Africa/Cairo'},
            {'name_en': 'Jordan', 'name_ar': 'الأردن', 'code': 'JOR', 'currency': 'JOD', 'timezone': 'Asia/Amman'},
            {'name_en': 'Kuwait', 'name_ar': 'الكويت', 'code': 'KWT', 'currency': 'KWD', 'timezone': 'Asia/Kuwait'},
            {'name_en': 'Qatar', 'name_ar': 'قطر', 'code': 'QAT', 'currency': 'QAR', 'timezone': 'Asia/Qatar'},
            {'name_en': 'Bahrain', 'name_ar': 'البحرين', 'code': 'BHR', 'currency': 'BHD', 'timezone': 'Asia/Bahrain'},
            {'name_en': 'Oman', 'name_ar': 'عمان', 'code': 'OMN', 'currency': 'OMR', 'timezone': 'Asia/Muscat'},
            {'name_en': 'Lebanon', 'name_ar': 'لبنان', 'code': 'LBN', 'currency': 'LBP', 'timezone': 'Asia/Beirut'},
        ]
        
        for country_data in countries_data:
            country, created = Country.objects.get_or_create(
                code=country_data['code'],
                defaults=country_data
            )
            if created:
                self.stdout.write(f'Created country: {country.name_en}')
        
        # Create delivery companies
        delivery_companies_data = [
            {'name_en': 'Aramex', 'name_ar': 'أرامكس', 'code': 'ARAMEX', 'base_cost': 15.00},
            {'name_en': 'DHL Express', 'name_ar': 'دي إتش إل إكسبريس', 'code': 'DHL', 'base_cost': 25.00},
            {'name_en': 'FedEx', 'name_ar': 'فيديكس', 'code': 'FEDEX', 'base_cost': 30.00},
            {'name_en': 'UPS', 'name_ar': 'يو بي إس', 'code': 'UPS', 'base_cost': 28.00},
            {'name_en': 'Emirates Post', 'name_ar': 'بريد الإمارات', 'code': 'EMPOST', 'base_cost': 8.00},
        ]
        
        for company_data in delivery_companies_data:
            company, created = DeliveryCompany.objects.get_or_create(
                code=company_data['code'],
                defaults=company_data
            )
            if created:
                # Add all countries to each company
                company.countries.set(Country.objects.all())
                self.stdout.write(f'Created delivery company: {company.name_en}')
        
        # Create default fees
        fees_data = [
            {'key': 'upsell_fee', 'value': '5.00', 'description': 'Default Upsell Fee'},
            {'key': 'confirmation_fee', 'value': '2.50', 'description': 'Default Confirmation Fee'},
            {'key': 'cancellation_fee', 'value': '10.00', 'description': 'Default Cancellation Fee'},
            {'key': 'fulfillment_fee', 'value': '3.00', 'description': 'Default Fulfillment Fee'},
            {'key': 'shipping_fee', 'value': '15.00', 'description': 'Default Shipping Fee'},
            {'key': 'return_fee', 'value': '8.00', 'description': 'Default Return Fee'},
            {'key': 'warehouse_fee', 'value': '1.50', 'description': 'Default Warehouse Fee'},
        ]
        
        for fee_data in fees_data:
            fee, created = SystemSetting.objects.get_or_create(
                key=fee_data['key'],
                defaults=fee_data
            )
            if created:
                self.stdout.write(f'Created fee setting: {fee.key} = ${fee.value}')
        
        # Create basic roles if they don't exist
        roles_data = [
            {'name': 'Super Admin', 'description': 'Full system access'},
            {'name': 'Admin', 'description': 'Administrative access'},
            {'name': 'Manager', 'description': 'Management access'},
            {'name': 'Staff', 'description': 'Basic staff access'},
            {'name': 'Call Center Agent', 'description': 'Call center operations'},
            {'name': 'Delivery Agent', 'description': 'Delivery operations'},
            {'name': 'Finance Manager', 'description': 'Financial operations'},
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            if created:
                self.stdout.write(f'Created role: {role.name}')
        
        # Create a default admin user if none exists
        if not User.objects.filter(is_staff=True).exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@atlas.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                is_staff=True,
                is_superuser=True
            )
            
            # Assign Super Admin role
            super_admin_role = Role.objects.filter(name='Super Admin').first()
            if super_admin_role:
                admin_user.roles.add(super_admin_role)
            
            self.stdout.write(f'Created default admin user: {admin_user.email}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up initial settings data!')
        ) 