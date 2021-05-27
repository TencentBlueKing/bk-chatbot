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
 * @file prod server
 * 静态资源
 * 模块渲染输出
 * 注入全局变量
 * 添加html模板引擎
 */
import express from 'express'
import path from 'path'
import fs from 'fs'
import artTemplate from 'express-art-template'
import history from 'connect-history-api-fallback'
import cookieParser from 'cookie-parser'
import axios from 'axios'
import ajaxMiddleware from './ajax-middleware'
import config from './config'

const app = new express()
const PORT = process.env.PORT || config.build.localDevPort || 5000
const http = axios.create({
	withCredentials: true
})

http.interceptors.response.use(response => response, error => Promise.reject(error))

// 注入全局变量
const GLOBAL_VAR = {
	SITE_URL: '',
	BK_STATIC_URL: '',
	REMOTE_STATIC_URL: process.env.BKPAAS_REMOTE_STATIC_URL || '',
	// 蓝鲸平台访问URL
	BKPAAS_URL: process.env.BKPAAS_URL || '',
	// 当前应用的环境，预发布环境为 stag，正式环境为 prod
	BKPAAS_ENVIRONMENT: process.env.BKPAAS_ENVIRONMENT || '',
	// EngineApp名称，拼接规则：bkapp-{appcode}-{BKPAAS_ENVIRONMENT}
	BKPAAS_ENGINE_APP_NAME: process.env.BKPAAS_ENGINE_APP_NAME || '',
	// MagicBox静态资源URL
	BKPAAS_REMOTE_STATIC_URL: process.env.BKPAAS_REMOTE_STATIC_URL || '',
	// 内部版对应ieod，外部版对应tencent，混合云版对应clouds
	BKPAAS_ENGINE_REGION: process.env.BKPAAS_ENGINE_REGION || '',
	// APP CODE
	BKPAAS_APP_ID: process.env.BKPAAS_APP_ID || ''
}

// APA 重定向回首页，由首页Route响应处理
// https://github.com/bripkens/connect-history-api-fallback#index
app.use(history({
	index: '/',
	rewrites: [
        {
            // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
            // 兼容 /cs/28aa9eda67644a6eb254d694d944307e/cluster/BCS-MESOS-10001/node/10.121.23.12 这样以 IP 结尾的 url
            // from: /\d+\.\d+\.\d+\.\d+$/,
            from: /\/(\d+\.)*\d+$/,
            to: '/'
        },
        {
            // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
            // 兼容 /bcs/projectId/app/214/taskgroups/0.application-1-13.test123.10013.1510806131114508229/containers/containerId
            from: /\/\/+.*\..*\//,
            to: '/'
        },
        {
        	from: '/user',
        	to: '/user'
        }
    ]
}))

app.use(cookieParser())

// 首页
app.get('/', (req, res) => {
	const index = path.join(__dirname, '../dist/index.html')
	res.render(index, GLOBAL_VAR)
})

app.get('/user', async (req, res) => {
	const token = req.cookies.bk_ticket
	try {
        const ret = await http.get(`/user/get_info?bk_ticket=${token}`)
        const resData = ret.data
        const loginCallbackURL = `/static/login_success.html?is_ajax=1`
        const loginURL = `/plain?app_code=1&c_url=${loginCallbackURL}`
        const result = {
            code: 0,
            data: null,
            message: resData.msg
        }

        if (resData.ret === 0) {
            const { username, avatar_url } = ret.data.data
            result.data = { username, avatar_url }
        } else {
        	result.code = 401
            result.login_url = loginURL
            res.status(401)
        }
        res.json(result)
    } catch (e) {
        throw new Error(e)
    }
})

app.use(ajaxMiddleware)
// 配置静态资源
app.use('/static', express.static(path.join(__dirname, '../dist/static')))

// 配置视图
app.set('views', path.join(__dirname, '../dist'))

// 配置模板引擎
// http://aui.github.io/art-template/zh-cn/docs/
app.engine('html', artTemplate)
app.set('view engine', 'html')

// 配置端口
app.listen(PORT, () => {
	console.log(`App is running in port ${PORT}`)
})
