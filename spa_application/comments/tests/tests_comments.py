import pytest

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from rest_framework import status
from django.core import exceptions

from company.business_logic import validate_image_size, MAX_IMAGE_SIZE
from company.models import Company
from address.models import Address


class TestValidatePassword:

    def test_passwords_incorrect(self, authenticated_client, randomizer):
        data = randomizer.company_data()
        data['password'] = randomizer.upp2_data()  # or         data.setdefault('password', randomizer.upp2_data())
        response = authenticated_client.post(reverse('company_new-list'), data=data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert response_json
        assert response.content == b'{"password":["Password incorrect."]}'
        assert response_json['password'] == ['Password incorrect.']


class TestBusinessLogic:

    def test_allowed_size_invalid(self):
        """ Next 2 str need for correct work 'pytest' command from Terminal.
        Important: 'absolute path' must be full and only like str without any functions() """
        with open(r'C:\Users\Silence\PycharmProjects\Web_Menu_DA\Web_Menu_DA\company\tests\Invalid_logo.jpg',
                  'rb') as f:
            read_data = f.read()
        test_logo = SimpleUploadedFile(name='Invalid_logo.jpg', content=read_data, content_type='image/jpeg')
        with pytest.raises(exceptions.ValidationError) as exc:
            validate_image_size(test_logo)
        assert f'Max file size is {str(MAX_IMAGE_SIZE)} KB' in str(exc.value)
        assert exc.type == exceptions.ValidationError

    def test_allowed_size_valid(self):
        """ Another way to set 'absolute path'. Need for correct work 'pytest' command from Terminal."""
        file_path = str(settings.BASE_DIR) + r'\company\tests\Valid_logo.jpg'
        test_logo = SimpleUploadedFile(
            name='Valid_logo.jpg',
            content=open(file_path, 'rb').read(),
            content_type='image/jpeg',
        )
        validate_image_size(test_logo)


class TestCreateCompanyView:
    def test_create_company_valid(self, authenticated_client_2, randomizer):
        company_data = randomizer.company_data()
        company_data['password'] = authenticated_client_2.user.user_password
        response = authenticated_client_2.post(reverse('company_new-list'), data=company_data, format='json')
        assert response.json()
        assert response.status_code == status.HTTP_201_CREATED
        for_check_create_company = Company.objects.get(owner_id=authenticated_client_2.user.id)
        assert for_check_create_company.legal_name == company_data['legal_name']
        assert not bool(for_check_create_company.logo.image)  # true if not False=bool((for_check_create_location.logo)
        assert for_check_create_company.legal_address_id is not None
        assert for_check_create_company.actual_address
        assert for_check_create_company.code_USREOU == company_data['code_USREOU']
        assert for_check_create_company.phone == company_data['phone']
        assert for_check_create_company.email == company_data['email']
        assert for_check_create_company.created_date is not None
        for_check_create_legal_address = Address.objects.get(id=for_check_create_company.legal_address_id)
        assert for_check_create_legal_address.country == company_data['legal_address']['country']
        assert for_check_create_legal_address.city == company_data['legal_address']['city']
        assert for_check_create_legal_address.street == company_data['legal_address']['street']
        assert for_check_create_legal_address.house_number == company_data['legal_address']['house_number']
        assert for_check_create_legal_address.flat_number == company_data['legal_address']['flat_number']
        for_check_create_actual_address = Address.objects.get(id=for_check_create_company.actual_address_id)
        assert for_check_create_actual_address.country == company_data['actual_address']['country']
        assert for_check_create_actual_address.city == company_data['actual_address']['city']
        assert for_check_create_actual_address.street == company_data['actual_address']['street']
        assert for_check_create_actual_address.house_number == company_data['actual_address']['house_number']
        assert for_check_create_actual_address.flat_number == company_data['actual_address']['flat_number']

    def test_update_company_valid(self, authenticated_client_2, randomizer, custom_company):
        data = randomizer.company_data()
        data['password'] = authenticated_client_2.user.user_password
        url = reverse('company_new-detail', kwargs={'pk': custom_company.id})
        response = authenticated_client_2.put(url, data=data, format='json')
        assert response.json()
        assert response.status_code == status.HTTP_200_OK
        for_check_create_company = Company.objects.get(id=custom_company.id)
        assert for_check_create_company.legal_name == data['legal_name']
        assert not bool(for_check_create_company.logo.image)
        assert for_check_create_company.legal_address
        assert for_check_create_company.actual_address_id is not None
        assert for_check_create_company.code_USREOU == data['code_USREOU']
        assert for_check_create_company.phone == data['phone']
        assert for_check_create_company.email == data['email']
        assert for_check_create_company.created_date is not None
        for_check_create_legal_address = Address.objects.get(id=for_check_create_company.legal_address_id)
        assert for_check_create_legal_address.country == data['legal_address']['country']
        assert for_check_create_legal_address.city == data['legal_address']['city']
        assert for_check_create_legal_address.street == data['legal_address']['street']
        assert for_check_create_legal_address.house_number == data['legal_address']['house_number']
        assert for_check_create_legal_address.flat_number == data['legal_address']['flat_number']
        for_check_create_actual_address = Address.objects.get(id=for_check_create_company.actual_address_id)
        assert for_check_create_actual_address.country == data['actual_address']['country']
        assert for_check_create_actual_address.city == data['actual_address']['city']
        assert for_check_create_actual_address.street == data['actual_address']['street']
        assert for_check_create_actual_address.house_number == data['actual_address']['house_number']
        assert for_check_create_actual_address.flat_number == data['actual_address']['flat_number']

    def test_update_another_client(self, authenticated_client, custom_company, randomizer):
        data = randomizer.company_data()
        data['password'] = custom_company.user_password
        url = reverse('company_new-detail', kwargs={'pk': custom_company.id})
        response = authenticated_client.put(url, data=data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()


class TestCompanyViewSet:
    def test_company_view_owner(self, authenticated_client_2, custom_company):
        response = authenticated_client_2.get(reverse('company'), format='json')
        response_json = response.json()
        data = response_json['results'][0]
        assert response_json
        assert response.status_code == status.HTTP_200_OK
        assert custom_company.id == data['id']
        assert custom_company.legal_name == data['legal_name']
        assert custom_company.legal_address
        assert custom_company.actual_address_id is not None
        assert custom_company.code_USREOU == data['code_USREOU']
        assert custom_company.phone == data['phone']
        assert custom_company.email == data['email']

    def test_company_view_pk_anoter_user(self, authenticated_client, custom_company):
        url = reverse('company_new-detail', kwargs={'pk': custom_company.id})
        response = authenticated_client.get(url, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()
