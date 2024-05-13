from rest_framework import serializers
from django.db import transaction

from company.models import Company
from address.models import Address
from address.serializers import AddressSerializer
from image.models import Image
from location.serializers import LocationSerializer
from company.business_logic import validate_image_size


class CompanySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')  # change visible info from owner_id to owner_email
    actual_address = AddressSerializer()
    legal_address = AddressSerializer()
    location = LocationSerializer(many=True)

    class Meta:
        # ordering = ['-id']  # Need to improve UnorderedObjectListWarning:
        # Pagination may yield inconsistent results with an unordered object_list
        model = Company
        fields = ['owner', 'id', 'legal_name', 'logo', 'legal_address', 'actual_address', 'code_USREOU', 'phone',
                  'email', 'location']


class CompanyImageSerializer(serializers.ModelSerializer):
    """Special Serializer to customize validators=[validate_image_size]"""
    image = serializers.ImageField(use_url=True, allow_null=True, validators=[validate_image_size])

    class Meta:
        model = Image
        fields = ['image']


class CreateCompanySerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    owner = serializers.ReadOnlyField(source='owner.email')
    legal_address = AddressSerializer()
    actual_address = AddressSerializer()
    logo = CompanyImageSerializer()

    class Meta:
        model = Company
        fields = ['id', 'owner', 'legal_name', 'logo', 'legal_address', 'actual_address', 'code_USREOU', 'phone',
                  'email', 'password']

    def create(self, validated_data):
        legal_address_data = validated_data.pop('legal_address')  # data from custom serializer
        actual_address_data = validated_data.pop('actual_address')  # data from custom serializer
        logo_data = validated_data.pop('logo', None)    # for correct work we must set default None if no image in logo
        with transaction.atomic():
            # atomic should stop other requests to db until we make the changes
            company = Company.objects.create(
                legal_address=Address.objects.create(**legal_address_data),
                actual_address=Address.objects.create(**actual_address_data),
                logo=Image.objects.create(image=None),  # need to create empty logo to set company_id
                **validated_data,
            )
            # company.logo.image.save don't work if logo/image None so we need to rule out these options
            if logo_data and logo_data.get('image'):
                company.logo.image.save(f'{company.legal_name}.jpg', logo_data['image'])
        return company

    def update(self, instance, validated_data):
        legal_address_data = validated_data.pop('legal_address')
        actual_address_data = validated_data.pop('actual_address')
        logo_data = validated_data.pop('logo')
        # make address and logo object separately by using custom 'Serializer'
        instance.legal_address = AddressSerializer().update(instance.legal_address, legal_address_data)
        instance.actual_address = AddressSerializer().update(instance.actual_address, actual_address_data)
        if logo_data and logo_data.get('image'):
            instance.logo.image.delete()
            instance.logo.image.save(f'{instance.legal_name}.jpg', logo_data['image'])
        else:
            instance.logo = CompanyImageSerializer().update(instance.logo, logo_data)
        return super().update(instance, validated_data)  # using default method - 'update' for company

    def validate(self, attrs):  # take from request context users password and check in database
        if user := self.context.get('user'):
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError({"password": "Password incorrect."})
        attrs.pop('password')  # we must delete password for correct work serializer
        return attrs
