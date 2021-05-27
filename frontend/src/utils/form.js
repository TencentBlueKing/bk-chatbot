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
 */

import http from '@/api'
import { messageError, messageSuccess } from '@/common/bkmagic'

// const methodsWithData = ['post', 'put', 'patch']

export async function submitRequest (mockUrl, params, dialog, obj, callback, method = 'post') {
    obj[dialog].loading = true
    try {
        const response = await http[method](mockUrl, params, {})
        if (response.result) {
            if (callback && typeof callback === 'function') {
                callback(obj)
            }
            messageSuccess(obj[dialog].msg)
        } else {
            messageError(response.message)
        }
    } catch (e) {
        if (e.hasOwnProperty('message') && e.message === 'OK') {
            if (callback && typeof callback === 'function') {
                callback(obj)
            }
            messageSuccess(obj[dialog].msg)
        }
    } finally {
        obj[dialog].loading = false
        obj[dialog].visible = false
    }
}

export function dialogOpen (obj, dialogName, callback) {
    if (callback && typeof callback === 'function') {
        callback(obj)
    }

    obj[dialogName].visible = true
}

export async function dialogValidate (obj, dialogName, formRef, callback) {
    if (callback && typeof callback === 'function') {
        callback(obj)
    }

    if (formRef !== '') {
        const result = await obj.$refs[formRef].validate().then(res => {
            return true
        }).catch(res => {
            return false
        })

        return result
    }

    return true
}

export async function dialogConfirm (obj, dialogName, formRef, method = 'post') {
    if (formRef !== '') {
        const result = await dialogValidate(obj, dialogName, formRef, null)
        if (!result) {
            return
        }
    }

    if (obj[dialogName].dataCallback && typeof obj[dialogName].dataCallback === 'function') {
        obj[dialogName].dataCallback(obj)
    }

    await submitRequest(obj[dialogName].mockUrl, obj[dialogName].params, dialogName, obj, obj[dialogName].submitCallback, method)
}

export function dialogClean (obj, dialogName) {
    if (obj[dialogName].tearCallback && typeof obj[dialogName].tearCallback === 'function') {
        obj[dialogName].tearCallback(obj)
    }
    obj.$refs[dialogName + 'Ref'].clearError()
}
