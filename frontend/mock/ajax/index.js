/**
 * TencentBlueKing is pleased to support the open source community by making
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
 * @file mock index module
 * @author
 */

import moment from 'moment'
import faker from 'faker'
import chalk from 'chalk'
import Mock from 'mockjs'

import { randomInt, sleep } from './util'

export async function response (getArgs, postArgs, req) {
    console.log(chalk.cyan('req', req.method))
    console.log(chalk.cyan('getArgs', JSON.stringify(getArgs, null, 0)))
    console.log(chalk.cyan('postArgs', JSON.stringify(postArgs, null, 0)))
    console.log()
    const invoke = getArgs.invoke
    if (invoke === 'getTableData') {
        // https://github.com/nuysoft/Mock/wiki/Getting-Started
        const list = Mock.mock({
            'list|10': [{
                // 属性 id 是一个自增数，起始值为 1，每次增 1
                'id|+1': 1,
                'ip': Mock.mock('@ip()'),
                'source': '微信',
                'status': '正常',
                'create_time': '2018-05-25 15:02:24',
                'children': [
                    {
                        'name': '用户管理',
                        'count': '23',
                        'creator': 'person2',
                        'create_time': '2017-10-10 11:12',
                        'desc': '用户管理'
                    },
                    {
                        'name': '模块管理',
                        'count': '2',
                        'creator': 'person1',
                        'create_time': '2017-10-10 11:12',
                        'desc': '无数据测试'
                    }
                ]
            }]
        })
        return {
            code: 0,
            data: list,
            message: 'ok'
        }
    }
    return {
        code: 0,
        data: {}
    }
}
