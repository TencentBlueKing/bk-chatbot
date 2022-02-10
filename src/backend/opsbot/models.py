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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON, DateTime

Base = declarative_base()


class BKExecutionLog(Base):
    __tablename__ = 'bk_execution_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bk_biz_id = Column(Integer, comment='业务ID')
    bk_platform = Column(String(length=64), comment='平台名称')
    bk_username = Column(String(length=128), comment='执行人')
    feature_name = Column(String(length=128), comment='对象名称')
    feature_id = Column(String(length=128), comment='对象ID')
    project_id = Column(String(length=128), comment='项目ID', default='')
    detail = Column(JSON, comment='执行详情', default={})
    created_at = Column(DateTime, comment='创建时间')

    def __repr__(self):
        return "<BKExecutionLog(bk_biz_id='%s', bk_platform='%s', feature_name='%s')>" % (
            self.bk_biz_id, self.bk_platform, self.feature_name)
