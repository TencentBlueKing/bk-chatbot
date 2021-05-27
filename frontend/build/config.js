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
 * @file config
 * @author
 */

import path from 'path'
import prodEnv from './prod.env'
import stagEnv from './stag.env'
import devEnv from './dev.env'

// 区分是测试环境还是正式环境
const onlineEnv = process.env.BKPAAS_ENVIRONMENT === 'stag' ? stagEnv : prodEnv

export default {
    build: {
        // env 会通过 webpack.DefinePlugin 注入到前端代码里
        env: onlineEnv,
        assetsRoot: path.resolve(__dirname, '../../static/dist'),
        assetsSubDirectory: 'static',
        assetsPublicPath: '{{BK_STATIC_URL}}',
        productionSourceMap: true,
        productionGzip: false,
        localDevPort: JSON.parse(onlineEnv.LOCAL_DEV_PORT),
        productionGzipExtensions: ['js', 'css'],
        bundleAnalyzerReport: process.env.npm_config_report
    },
    dev: {
        // env 会通过 webpack.DefinePlugin 注入到前端代码里
        env: devEnv,
        // 这里用 JSON.parse 是因为 dev.env.js 里有一次 JSON.stringify，dev.env.js 里的 JSON.stringify 不能去掉
        localDevUrl: JSON.parse(devEnv.LOCAL_DEV_URL),
        localDevPort: JSON.parse(devEnv.LOCAL_DEV_PORT),
        assetsSubDirectory: 'static',
        assetsPublicPath: '/',
        proxyTable: {},
        cssSourceMap: false,
        autoOpenBrowser: false
    }
}
