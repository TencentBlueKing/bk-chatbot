<!--
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
-->

<template>
    <div class="main-content">
        <div class="app-container">
        </div>
        <div class="app-content">
            <div class="wrapper">
                <bk-container :col="12" :gutter="4">
                    <bk-row class="mb15">
                        <bk-col :span="9">
                            <div class="content">
                                <bk-button
                                    theme="primary"
                                    title="注册"
                                    ext-cls="opsbot-button"
                                    @click="dialogOpen(botYW, 'createBot', createBot.openCallback(botYW))"
                                    disabled>
                                    注册</bk-button>
                            </div>
                        </bk-col>
                        <bk-col :span="3">
                            <div class="content">
                                <bk-search-select clearable :show-popover-tag-change="true"
                                    :data="botTableData.searchData.data"
                                    v-model="botTableData.searchData.query" :show-condition="false"
                                    @change="getTableData(1, botTableData.searchData.query)"
                                    @clear="getTableData(1, botTableData.searchData.query)"></bk-search-select>
                            </div>
                        </bk-col>
                    </bk-row>
                    <bk-row>
                        <bk-col :span="12">
                            <bk-table
                                :data="botTableData.data"
                                size="small"
                                :pagination="botTableData.pagination"
                                v-bkloading="{ isLoading: botTableData.loading, theme: 'primary' }"
                                @page-change="handleTablePageChangeAsync"
                                @selection-change="handleTableSelectionChange($event, botYW, 'botTableData')">
                                <bk-table-column label="名称" prop="bot_name">
                                    <template slot-scope="scope">
                                        <!--
                                        <bk-button class="mr10" text theme="primary">{{ scope.row.bot_name }}</bk-button>
                                        -->
                                        <span>{{ scope.row.bot_name }}</span>
                                    </template>
                                </bk-table-column>
                                <bk-table-column label="ID" prop="bot_id"></bk-table-column>
                                <bk-table-column label="类型" prop="bot_type"></bk-table-column>
                                <bk-table-column label="创建人" prop="created_by"></bk-table-column>
                                <bk-table-column label="修改时间" prop="updated_at"></bk-table-column>
                                <bk-table-column label="操作" width="150">
                                    <template slot-scope="scope">
                                        <bk-button
                                            class="mr10"
                                            theme="primary"
                                            text
                                            :ref="'bot-' + scope.$index"
                                            disabled>编辑</bk-button>
                                        <bk-popconfirm
                                            trigger="click"
                                            :confirm-button-is-text="false"
                                            confirm-text="确定"
                                            cancel-text="取消"
                                            @confirm="dialogConfirm(botYW, 'deleteBot', '', 'delete')">
                                            <div slot="content">
                                                <div>
                                                    <i class="bk-icon icon-info-circle-shape pr5" style="color: red;"></i>
                                                    确认删除该机器人: {{ scope.row.bot_name }}
                                                </div>
                                            </div>
                                            <bk-button
                                                class="mr10"
                                                theme="primary"
                                                text
                                                @click="dialogOpen(botYW, 'deleteBot', deleteBot.openCallback(botYW, scope.row))"
                                                disabled>删除</bk-button>
                                        </bk-popconfirm>
                                    </template>
                                </bk-table-column>
                            </bk-table>
                        </bk-col>
                    </bk-row>
                </bk-container>
            </div>
        </div>
        <bk-dialog v-model="createBot.visible"
            theme="primary"
            width="500"
            header-position="left"
            :title="createBot.title"
            :auto-close="false"
            :loading="createBot.loading"
            @confirm="dialogConfirm(botYW, 'createBot', 'createBotRef', createBot.method)"
            @after-leave="dialogClean(botYW, 'createBot')">
            <bk-form :label-width="200" form-type="vertical" ref="createBotRef"
                :model="createBot.form.data"
                :rules="createBot.form.rules">
                <bk-form-item label="类型" :required="true" property="botType">
                    <bk-select v-model="createBot.form.data.botType" searchable placeholder="请选择机器人类型">
                        <bk-option id="default" name="OPSBOT"></bk-option>
                        <bk-option id="qq" name="QQ"></bk-option>
                        <bk-option id="xwork" name="企业微信"></bk-option>
                        <bk-option id="wechat" name="微信"></bk-option>
                        <bk-option id="slack" name="Slack" disabled></bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="名称" :required="true" property="botName">
                    <bk-input v-model="createBot.form.data.botName" placeholder="请输入新名称"></bk-input>
                </bk-form-item>
                <bk-form-item label="WebHook" :required="true" property="xworkWebHook" v-if="createBot.form.data.botType === 'xwork'">
                    <bk-input v-model="createBot.form.data.xworkWebHook" placeholder="请输入回调地址"></bk-input>
                </bk-form-item>
                <bk-form-item label="Token" :required="true" property="xworkToken" v-if="createBot.form.data.botType === 'xwork'">
                    <bk-input v-model="createBot.form.data.xworkToken" placeholder="请输入Token"></bk-input>
                </bk-form-item>
                <bk-form-item label="EncodingAESKey" :required="true" property="xworkEncodingAESKey" v-if="createBot.form.data.botType === 'xwork'">
                    <bk-input v-model="createBot.form.data.xworkEncodingAESKey" placeholder="请输入AesKey"></bk-input>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>

<script>
    import { randomStr } from '../../utils/stdlib'
    import { dialogOpen, dialogClean, dialogConfirm } from '../../utils/form'
    import { handleTableSelectionChange } from '../../utils/table'

    export default {
        components: {
        },
        props: {
            'bizId': {
                type: String
            }
        },
        data () {
            return {
                botYW: null,
                botTableData: {
                    pagination: {
                        current: 1,
                        count: 500,
                        'limit-list': [10],
                        limit: 10
                    },
                    raw: [],
                    data: [],
                    multipleSelection: [],
                    title: [],
                    loading: false,
                    searchData: {
                        data: [
                            {
                                name: 'ID',
                                id: '1',
                                prop: 'bot_id',
                                multiable: false,
                                children: []
                            },
                            {
                                name: '名称',
                                id: '2',
                                prop: 'bot_name',
                                multiable: false,
                                children: []
                            },
                            {
                                name: '类型',
                                id: '3',
                                prop: 'bot_type',
                                multiable: false,
                                children: []
                            },
                            {
                                name: '创建人',
                                id: '4',
                                prop: 'create_by',
                                multiable: false,
                                children: []
                            }
                        ],
                        query: '',
                        result: []
                    }
                },
                createBot: {
                    visible: false,
                    loading: false,
                    msg: '机器人创建成功',
                    title: '机器人创建',
                    method: 'post',
                    form: {
                        data: {
                            botId: '',
                            botName: '',
                            botType: 'default',
                            xworkWebHook: '',
                            xworkToken: '',
                            xworkEncodingAESKey: ''
                        },
                        rules: {
                            botName: [
                                { required: true, message: '请输机器人名称', trigger: 'blur' }
                            ],
                            botType: [
                                { required: true, message: '请选择机器人类型', trigger: 'change' }
                            ]
                        }
                    },
                    mockUrl: `${AJAX_URL_PREFIX}/api/v1/` + this.bizId + `/bot/?${AJAX_MOCK_PARAM}=intent&invoke=common`,
                    params: {},
                    openCallback: (obj, row) => {
                        obj.createBot.mockUrl = `${AJAX_URL_PREFIX}/api/v1/` + obj.bizId + `/bot/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                    },
                    dataCallback: (obj) => {
                        obj.createBot.params['biz_id'] = obj.bizId
                        obj.createBot.params['bot_id'] = obj.createBot.form.data.botId || randomStr(false, 16)
                        obj.createBot.params['bot_type'] = obj.createBot.form.data.botType
                        obj.createBot.params['bot_name'] = obj.createBot.form.data.botName
                        obj.createBot.params['biz_name'] = '-'
                    },
                    submitCallback: (obj) => {
                        obj.getTableData(1)
                    },
                    tearCallback: (obj) => {
                        obj.createBot.form.data = {
                            botId: '',
                            botName: '',
                            botType: 'default',
                            xworkWebHook: '',
                            xworkToken: '',
                            xworkEncodingAESKey: ''
                        }
                        obj.createBot.params = {}
                    }
                },
                deleteBot: {
                    visible: false,
                    msg: '机器人删除成功',
                    loading: false,
                    method: 'delete',
                    mockUrl: ``,
                    params: {},
                    openCallback: (obj, row) => {
                        obj.deleteBot.mockUrl = `${AJAX_URL_PREFIX}/api/v1/` + obj.bizId + `/bot/` + row.id + `/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                    },
                    submitCallback: (obj) => {
                        obj.getTableData(1)
                    }
                }
            }
        },
        watch: {
            bizId: function (val) {
                this.init()
            }
        },
        mounted () {
            this.$emit('doHeader', false)
            this.init()
        },
        methods: {
            handleTableSelectionChange,
            dialogOpen,
            dialogClean,
            dialogConfirm,
            init () {
                this.botYW = this
                if (this.bizId !== '' && typeof this.bizId !== 'undefined') {
                    this.getTableData(1)
                }
            },
            goIntent (scope) {
                this.$router.push({
                    path: `intent/list/${scope.row.id}`
                })
            },
            handleTablePageChangeAsync (page) {
                this.getTableData(page, this.botTableData.searchData.query)
            },
            async getTableData (page, filter) {
                const params = {
                    bizId: this.bizId,
                    data: {
                        'biz_id': this.bizId,
                        'page': page
                    }
                }
                if (typeof filter === 'object') {
                    filter.forEach((item) => {
                        params.data[item.prop] = item.values.map((k) => {
                            return k.id
                        }).join(',')
                    })
                }

                try {
                    this.botTableData.loading = true
                    const response = await this.$store.dispatch('bot/getBotTableData', params, {})
                    this.botTableData.raw = response.data.results || []
                    this.botTableData.data = JSON.parse(JSON.stringify(this.botTableData.raw))
                    this.botTableData.pagination.count = response.data.count
                    this.botTableData.pagination.current = page
                    this.botTableData.loading = false
                } catch (e) {
                    console.error(e)
                }
            }
        }
    }
</script>

<style>
    @import './index.css';
</style>
