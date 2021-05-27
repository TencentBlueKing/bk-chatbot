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

export function getPromiseResult (obj, form) {
    const p = new Promise((resolve, reject) => {
        obj.$refs[form].validate(valid => {
            if (valid) {
                resolve()
            }
        })
    })

    return p
}

export function randomStr (randomFlag, min, max) {
    let str = ''
    let range = min
    const arr = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    if (randomFlag) {
        range = Math.round(Math.random() * (max - min)) + min
    }
    for (let i = 0; i < range; i++) {
        const pos = Math.round(Math.random() * (arr.length - 1))
        str += arr[pos]
    }
    return str
}

export function goPage (obj, path, blank = false, query = {}) {
    if (blank) {
        const routeData = obj.$router.resolve({ path: path, query: query })
        window.open(routeData.href, '_blank')
    } else {
        obj.$router.push({ path: path })
    }
}
