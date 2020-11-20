import datetime
import urllib.parse

import pytest
from django.urls import reverse
from pytz import UTC

from hours.authentication import calculate_signature, join_params
from hours.models import SignedAuthEntry
from users.models import User


@pytest.mark.django_db
def test_get_auth_required_unauthenticated(api_client):
    url = reverse("auth_required_test-list")
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_get_auth_required_header_invalid_signature(
    api_client, data_source, signed_auth_key_factory
):
    signed_auth_key_factory(data_source=data_source)

    url = reverse("auth_required_test-list")

    authz_string = (
        "haukisigned"
        " source=" + data_source.id + "&username=test_user"
        "&created_at=2020-10-01T06%3A35%3A00.917Z"
        "&valid_until=2020-11-01T06%3A45%3A00.917Z"
        "&signature=invalid_signature"
    )

    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 403
    assert str(response.data["detail"]) == "Invalid signature"


@pytest.mark.django_db
def test_get_auth_required_header_invalid_created_at(
    api_client, data_source, signed_auth_key_factory
):
    signed_auth_key = signed_auth_key_factory(data_source=data_source)

    url = reverse("auth_required_test-list")

    data = {
        "source": data_source.id,
        "username": "test_user",
        "created_at": "2030-01-01T10:10:10.000Z",
        "valid_until": "2030-01-01T10:20:10.000Z",
    }

    source_string = join_params(data)
    signature = calculate_signature(signed_auth_key.signing_key, source_string)

    authz_string = "haukisigned " + urllib.parse.urlencode(
        {**data, "signature": signature}
    )

    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 403
    assert str(response.data["detail"]) == "Invalid created_at"


@pytest.mark.django_db
def test_get_auth_required_header_invalid_valid_until(
    api_client, data_source, signed_auth_key_factory
):
    signed_auth_key = signed_auth_key_factory(data_source=data_source)

    url = reverse("auth_required_test-list")

    data = {
        "source": data_source.id,
        "username": "test_user",
        "created_at": "2020-01-01T10:10:10.000Z",
        "valid_until": "2000-01-01T10:20:10.000Z",
    }

    source_string = join_params(data)
    signature = calculate_signature(signed_auth_key.signing_key, source_string)

    authz_string = "haukisigned " + urllib.parse.urlencode(
        {**data, "signature": signature}
    )

    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 403
    assert str(response.data["detail"]) == "Invalid valid_until"


@pytest.mark.django_db
def test_get_auth_required_header_authenticated(
    api_client, data_source, signed_auth_key_factory
):
    signed_auth_key = signed_auth_key_factory(data_source=data_source)

    url = reverse("auth_required_test-list")

    now = datetime.datetime.utcnow()

    data = {
        "source": data_source.id,
        "username": "test_user",
        "created_at": now.isoformat() + "Z",
        "valid_until": (now + datetime.timedelta(minutes=10)).isoformat() + "Z",
    }

    source_string = join_params(data)
    signature = calculate_signature(signed_auth_key.signing_key, source_string)

    authz_string = "haukisigned " + urllib.parse.urlencode(
        {**data, "signature": signature}
    )

    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 200
    assert response.data["username"] == "test_user"


@pytest.mark.django_db
def test_join_user_to_organization(
    api_client, data_source_factory, signed_auth_key_factory, organization_factory
):
    data_source = data_source_factory(id="test")
    signed_auth_key = signed_auth_key_factory(data_source=data_source)
    org = organization_factory(data_source=data_source, origin_id=1234)

    url = reverse("auth_required_test-list")

    now = datetime.datetime.utcnow()

    data = {
        "source": data_source.id,
        "username": "test_user",
        "created_at": now.isoformat() + "Z",
        "valid_until": (now + datetime.timedelta(minutes=10)).isoformat() + "Z",
        "organization": org.id,
    }

    signature = calculate_signature(signed_auth_key.signing_key, join_params(data))

    authz_string = "haukisigned " + urllib.parse.urlencode(
        {**data, "signature": signature}
    )

    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 200
    assert response.data["username"] == "test_user"

    user = User.objects.get(username="test_user")

    assert user.organization_memberships.count() == 1


@pytest.mark.django_db
def test_join_user_to_organization_existing_user(
    api_client,
    user_factory,
    data_source_factory,
    signed_auth_key_factory,
    organization_factory,
):
    user = user_factory(username="test_user")

    data_source = data_source_factory(id="test")
    signed_auth_key = signed_auth_key_factory(data_source=data_source)
    org = organization_factory(data_source=data_source, origin_id=1234)

    url = reverse("auth_required_test-list")

    now = datetime.datetime.utcnow()

    data = {
        "source": data_source.id,
        "username": user.username,
        "created_at": now.isoformat() + "Z",
        "valid_until": (now + datetime.timedelta(minutes=10)).isoformat() + "Z",
        "organization": org.id,
    }

    signature = calculate_signature(signed_auth_key.signing_key, join_params(data))

    authz_string = "haukisigned " + urllib.parse.urlencode(
        {**data, "signature": signature}
    )

    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 200
    assert response.data["username"] == "test_user"

    assert User.objects.count() == 1

    assert user.organization_memberships.count() == 1


@pytest.mark.django_db
def test_join_user_to_organization_existing_user_and_organisation(
    api_client,
    user_factory,
    data_source_factory,
    signed_auth_key_factory,
    organization_factory,
):
    user = user_factory(username="test_user")

    data_source = data_source_factory(id="test")
    signed_auth_key = signed_auth_key_factory(data_source=data_source)
    org = organization_factory(data_source=data_source, origin_id=1234)

    user.organization_memberships.add(org)

    url = reverse("auth_required_test-list")

    now = datetime.datetime.utcnow()

    data = {
        "source": data_source.id,
        "username": user.username,
        "created_at": now.isoformat() + "Z",
        "valid_until": (now + datetime.timedelta(minutes=10)).isoformat() + "Z",
        "organization": org.id,
    }

    signature = calculate_signature(signed_auth_key.signing_key, join_params(data))

    authz_string = "haukisigned " + urllib.parse.urlencode(
        {**data, "signature": signature}
    )

    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 200
    assert response.data["username"] == "test_user"

    assert User.objects.count() == 1

    assert user.organization_memberships.count() == 1


@pytest.mark.django_db
def test_join_user_to_organization_invalid_org(
    api_client, data_source, signed_auth_key_factory
):
    signed_auth_key = signed_auth_key_factory(data_source=data_source)

    url = reverse("auth_required_test-list")

    now = datetime.datetime.utcnow()

    data = {
        "source": data_source.id,
        "username": "test_user",
        "created_at": now.isoformat() + "Z",
        "valid_until": (now + datetime.timedelta(minutes=10)).isoformat() + "Z",
        "organization": "test:2345",
    }

    signature = calculate_signature(signed_auth_key.signing_key, join_params(data))

    authz_string = "haukisigned " + urllib.parse.urlencode(
        {**data, "signature": signature}
    )

    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 200
    assert response.data["username"] == "test_user"

    user = User.objects.get(username="test_user")

    assert user.organization_memberships.count() == 0


@pytest.mark.django_db
def test_join_user_to_organization_wrong_data_source_org(
    api_client, data_source_factory, organization_factory, signed_auth_key_factory
):
    data_source1 = data_source_factory()
    data_source2 = data_source_factory()

    org = organization_factory(data_source=data_source2, origin_id=1234)

    signed_auth_key = signed_auth_key_factory(data_source=data_source1)

    url = reverse("auth_required_test-list")

    now = datetime.datetime.utcnow()

    data = {
        "source": data_source1.id,
        "username": "test_user",
        "created_at": now.isoformat() + "Z",
        "valid_until": (now + datetime.timedelta(minutes=10)).isoformat() + "Z",
        "organization": org.id,
    }

    signature = calculate_signature(signed_auth_key.signing_key, join_params(data))

    authz_string = "haukisigned " + urllib.parse.urlencode(
        {**data, "signature": signature}
    )

    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 200
    assert response.data["username"] == "test_user"

    user = User.objects.get(username="test_user")

    assert user.organization_memberships.count() == 0


@pytest.mark.django_db
def test_signed_auth_entry_not_invalidated(
    api_client, data_source, signed_auth_key_factory
):
    signed_auth_key = signed_auth_key_factory(data_source=data_source)

    url = reverse("auth_required_test-list")

    now = datetime.datetime.utcnow()
    valid_until = now + datetime.timedelta(minutes=10)

    data = {
        "source": data_source.id,
        "username": "test_user",
        "created_at": now.isoformat() + "Z",
        "valid_until": valid_until.isoformat() + "Z",
    }

    signature = calculate_signature(signed_auth_key.signing_key, join_params(data))

    authz_string = "haukisigned " + urllib.parse.urlencode(
        {**data, "signature": signature}
    )

    # Check that auth works
    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 200
    assert response.data["username"] == "test_user"

    # Add a non invalidated entry to the database
    SignedAuthEntry.objects.create(
        signature=signature,
        created_at=now.replace(tzinfo=UTC),
        valid_until=valid_until.replace(tzinfo=UTC),
    )

    # Check that auth still works
    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 200
    assert response.data["username"] == "test_user"


@pytest.mark.django_db
def test_invalidate_signature_success_header_params(
    api_client, data_source, signed_auth_key_factory
):
    url = reverse("auth_required_test-list")

    signed_auth_key = signed_auth_key_factory(data_source=data_source)

    now = datetime.datetime.utcnow()

    valid_until = now + datetime.timedelta(minutes=10)

    data = {
        "source": data_source.id,
        "username": "test_user",
        "created_at": now.isoformat() + "Z",
        "valid_until": valid_until.isoformat() + "Z",
    }

    signature = calculate_signature(signed_auth_key.signing_key, join_params(data))

    authz_string = "haukisigned " + urllib.parse.urlencode(
        {**data, "signature": signature}
    )

    # Check that auth works
    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 200
    assert response.data["username"] == "test_user"

    # Invalidate the signature
    invalidate_url = reverse("invalidate_hauki_auth_signature")
    response = api_client.post(invalidate_url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 200
    assert response.data == {"success": True}

    signed_auth_entry = SignedAuthEntry.objects.get(signature=signature)

    assert signed_auth_entry.created_at == now.replace(tzinfo=UTC)
    assert signed_auth_entry.valid_until == valid_until.replace(tzinfo=UTC)

    # Verify that the auth no longer works
    response = api_client.get(url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 403


@pytest.mark.django_db
def test_invalidate_signature_success_query_params(
    api_client, data_source, signed_auth_key_factory
):
    signed_auth_key = signed_auth_key_factory(data_source=data_source)

    url = reverse("auth_required_test-list")

    now = datetime.datetime.utcnow()

    data = {
        "source": data_source.id,
        "username": "test_user",
        "created_at": now.isoformat() + "Z",
        "valid_until": (now + datetime.timedelta(minutes=10)).isoformat() + "Z",
    }

    signature = calculate_signature(signed_auth_key.signing_key, join_params(data))

    authz_string = "?" + urllib.parse.urlencode({**data, "signature": signature})

    # Check that auth works
    response = api_client.get(f"{url}{authz_string}")

    assert response.status_code == 200
    assert response.data["username"] == "test_user"

    # Invalidate the signature
    invalidate_url = reverse("invalidate_hauki_auth_signature")
    response = api_client.post(f"{invalidate_url}{authz_string}")

    assert response.status_code == 200
    assert response.data == {"success": True}

    # Verify that the auth no longer works
    response = api_client.get(f"{url}{authz_string}")

    assert response.status_code == 403


@pytest.mark.django_db
def test_invalidate_signature_no_params(api_client):

    # Invalidate the signature
    invalidate_url = reverse("invalidate_hauki_auth_signature")
    response = api_client.post(invalidate_url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_invalidate_signature_invalid_params(
    api_client, data_source, signed_auth_key_factory
):
    signed_auth_key = signed_auth_key_factory(data_source=data_source)

    now = datetime.datetime.utcnow()

    data = {
        "source": data_source.id,
        # username missing
        "created_at": now.isoformat() + "Z",
        "valid_until": (now + datetime.timedelta(minutes=10)).isoformat() + "Z",
    }

    signature = calculate_signature(signed_auth_key.signing_key, join_params(data))

    authz_string = "haukisigned " + urllib.parse.urlencode(
        {**data, "signature": signature}
    )

    # Invalidate the signature
    invalidate_url = reverse("invalidate_hauki_auth_signature")
    response = api_client.post(invalidate_url, HTTP_AUTHORIZATION=authz_string)

    assert response.status_code == 403
