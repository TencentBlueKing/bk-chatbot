# -*- coding: utf-8 -*-

"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云PaaS平台社区版 (BlueKing PaaSCommunity Edition) available.
Copyright (C) 2017-2018 THL A29 Limited,
a Tencent company. All rights reserved.
Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from http.cookies import SimpleCookie

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory
from faker import Faker

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture()
def fake_biz_id(faker) -> int:
    """
    业务CC_ID
    """
    return faker.random_int()


@pytest.fixture()
def login_exempt_info() -> dict:
    """
    免登陆信息
    """

    return dict(
        bk_app_code=settings.APP_CODE,
        bk_app_secret=settings.SECRET_KEY,
    )


@pytest.fixture()
def faker() -> Faker:
    yield Faker()


@pytest.fixture
def fake_user(faker) -> User:
    fake_user = User.objects.create(username=faker.first_name(), is_active=True)
    fake_user.set_password(faker.uuid4())
    fake_user.save()
    return fake_user


@pytest.fixture()
def admin_client(faker) -> Client:
    class Context:
        """
        用户登录上下文
        """

        token = faker.sha1(raw_output=False)
        cookies = dict(
            bk_token=token,
            bk_ticket=token,
        )

    client = Client(
        HTTP_App_Id=settings.APP_CODE,
        HTTP_App_Token=settings.SECRET_KEY,
    )

    client.cookies = SimpleCookie(Context().cookies)
    return client


@pytest.fixture()
def factory() -> RequestFactory:
    yield RequestFactory()
