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
                                    theme="default"
                                    title="设置绑定"
                                    :hover-theme="'primary'"
                                    @click="dialogOpen(groupYW, 'bindBizToGroup', bindBizToGroup.openCallback(groupYW))">
                                    设置绑定</bk-button>
                            </div>
                        </bk-col>
                        <bk-col :span="3">
                            <div class="content">
                                <bk-search-select clearable :show-popover-tag-change="true"
                                    :data="groupTableData.searchData.data"
                                    v-model="groupTableData.searchData.query" :show-condition="false"
                                    @change="getGroupTableData(1, groupTableData.searchData.query)"
                                    @clear="getGroupTableData(1, groupTableData.searchData.query)"></bk-search-select>
                            </div>
                        </bk-col>
                    </bk-row>
                    <bk-row>
                        <bk-col :span="12">
                            <bk-table
                                :data="groupTableData.data"
                                :pagination="groupTableData.pagination"
                                v-bkloading="{ isLoading: groupTableData.loading, theme: 'primary' }"
                                @page-change="handleTablePageChangeAsync"
                                @selection-change="handleTableSelectionChange($event, groupYW, 'groupTableData')"
                                ext-cls="opsbot-group-table">
                                <bk-table-column type="selection" width="60"></bk-table-column>
                                <bk-table-column label="群名称" prop="chat_group_name"></bk-table-column>
                                <bk-table-column label="群类型" prop="chat_bot_type"></bk-table-column>
                                <bk-table-column label="群ID" prop="chat_group_id"></bk-table-column>
                                <bk-table-column label="更新人" prop="updated_by"></bk-table-column>
                                <bk-table-column label="更新时间" prop="updated_at"></bk-table-column>
                                <bk-table-column label="操作" width="150">
                                    <template slot-scope="scope">
                                        <bk-button
                                            class="mr10"
                                            theme="primary"
                                            text
                                            @click="dialogOpen(groupYW, 'bindBizToGroup', bindBizToGroup.openCallback(groupYW, scope.row))"
                                            :ref="'group-' + scope.$index">编辑</bk-button>
                                        <bk-popconfirm
                                            trigger="click"
                                            :confirm-button-is-text="false"
                                            confirm-text="确定"
                                            cancel-text="取消"
                                            @confirm="dialogConfirm(groupYW, 'unBindBizToGroup', '', 'delete')">
                                            <div slot="content">
                                                <div>
                                                    <i class="bk-icon icon-info-circle-shape pr5" style="color: red;"></i>
                                                    确认解除群绑定: {{ scope.row.chat_group_id }}
                                                </div>
                                            </div>
                                            <bk-button
                                                class="mr10"
                                                theme="primary"
                                                text
                                                @click="dialogOpen(groupYW, 'unBindBizToGroup', unBindBizToGroup.openCallback(groupYW, scope.row))">删除</bk-button>
                                        </bk-popconfirm>
                                    </template>
                                </bk-table-column>
                            </bk-table>
                        </bk-col>
                    </bk-row>
                </bk-container>
            </div>
        </div>
        <bk-dialog v-model="bindBizToGroup.visible"
            theme="primary"
            width="500"
            header-position="left"
            :title="bindBizToGroup.title"
            :auto-close="false"
            :loading="bindBizToGroup.loading"
            @confirm="dialogConfirm(groupYW, 'bindBizToGroup', 'bindBizToGroupRef', bindBizToGroup.method)"
            @after-leave="dialogClean(groupYW, 'bindBizToGroup')">
            <bk-form :label-width="200" form-type="vertical" ref="bindBizToGroupRef"
                :model="bindBizToGroup.form.data"
                :rules="bindBizToGroup.form.rules">
                <bk-form-item label="类型" :required="true" property="chat_bot_type">
                    <bk-select v-model="bindBizToGroup.form.data.chat_bot_type" searchable placeholder="请选择机器人类型" disabled>
                        <bk-option id="default" name="OPSBOT"></bk-option>
                        <bk-option id="qq" name="QQ"></bk-option>
                        <bk-option id="xwork" name="企业微信"></bk-option>
                        <bk-option id="wechat" name="微信"></bk-option>
                        <bk-option id="slack" name="Slack" disabled></bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="业务" :required="true" property="biz_id">
                    <bk-select v-model="bindBizToGroup.form.data.biz_id" searchable placeholder="请选择机器业务" disabled>
                        <bk-option v-for="item in bizData.data" :key="item.bk_biz_id" :id="item.bk_biz_id" :name="item.bk_biz_name"></bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="群ID"
                    :required="true"
                    property="chat_group_id"
                    v-if="bindBizToGroup.method === 'post'"
                    :desc-type="'icon'"
                    desc="获取群ID方法：<br />
                    1.群中添加服务号：opsbot3.0机器人<br />
                    2.手动@opsbot3.0 并输入关键字'群ID'<br />
                    3.将获取到的群ID粘贴到输入框">
                    <bk-input v-model="bindBizToGroup.form.data.chat_group_id" placeholder="请输入群ID"></bk-input>
                </bk-form-item>
                <bk-form-item label="群名称" :required="true" property="chat_group_name">
                    <bk-input v-model="bindBizToGroup.form.data.chat_group_name" placeholder="请输入群名称"></bk-input>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>

<script>
    import { handleTableSelectionChange } from '../../utils/table'
    import { dialogOpen, dialogClean, dialogConfirm } from '../../utils/form'

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
                groupYW: null,
                groupTableData: {
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
                    filter: {
                        date: []
                    },
                    render: false,
                    loading: false,
                    searchData: {
                        data: [
                            {
                                name: '更新人',
                                id: '1',
                                prop: 'updated_by',
                                multiable: false,
                                children: []
                            },
                            {
                                name: '群ID',
                                id: '2',
                                prop: 'chat_group_id',
                                multiable: false,
                                children: []
                            },
                            {
                                name: '群名称',
                                id: '3',
                                prop: 'chat_group_name',
                                multiable: false,
                                children: []
                            }
                        ],
                        query: '',
                        result: []
                    }
                },
                bizData: {
                    data: []
                },
                bindBizToGroup: {
                    visible: false,
                    msg: '业务绑定成功',
                    loading: false,
                    title: '业务绑定',
                    method: 'post',
                    data: [],
                    form: {
                        data: {
                            id: -1,
                            chat_bot_type: 'xwork',
                            biz_id: '',
                            biz_name: '',
                            chat_group_id: '',
                            chat_group_name: ''
                        },
                        rules: {
                            chat_bot_type: [
                                { required: true, message: '请选择群类型', trigger: 'blur' }
                            ],
                            biz_id: [
                                { required: true, message: '请选择业务', trigger: 'blur' }
                            ],
                            chat_group_id: [
                                { required: true, message: '请输入群ID', trigger: 'blur' },
                                {
                                    validator: this.checkGroupId,
                                    message: '该群已被其他业务绑定',
                                    trigger: 'blur'
                                }
                            ],
                            chat_group_name: [
                                { required: true, message: '请输入群群名称', trigger: 'blur' }
                            ]
                        }
                    },
                    mockUrl: `${AJAX_URL_PREFIX}/api/v1/chat_bind/?${AJAX_MOCK_PARAM}=intent&invoke=common`,
                    params: {},
                    openCallback: (obj, row) => {
                        if (typeof row !== 'undefined') {
                            obj.bindBizToGroup.form.data.chat_group_id = row.chat_group_id
                            obj.bindBizToGroup.form.data.chat_group_name = row.chat_group_name
                            obj.bindBizToGroup.mockUrl = `${AJAX_URL_PREFIX}/api/v1/chat_bind/` + row.chat_group_id + `/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                            obj.bindBizToGroup.method = 'patch'
                        } else {
                            obj.bindBizToGroup.form.data.chat_group_id = ''
                            obj.bindBizToGroup.mockUrl = `${AJAX_URL_PREFIX}/api/v1/chat_bind/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                            obj.bindBizToGroup.method = 'post'
                        }
                        obj.bindBizToGroup.form.data.biz_id = obj.bizId
                        obj.getBiz()
                    },
                    dataCallback: (obj) => {
                        obj.bindBizToGroup.params['biz_id'] = obj.bindBizToGroup.form.data.biz_id
                        obj.bindBizToGroup.params['chat_bot_type'] = obj.bindBizToGroup.form.data.chat_bot_type
                        const r = obj.bizData.data.find(e => e['bk_biz_id'] === parseInt(obj.bindBizToGroup.form.data.biz_id))
                        if (typeof r !== 'undefined') {
                            obj.bindBizToGroup.params['biz_name'] = r['bk_biz_name']
                        }
                        if (obj.bindBizToGroup.form.data.chat_group_id !== '') {
                            obj.bindBizToGroup.params['chat_group_id'] = obj.bindBizToGroup.form.data.chat_group_id
                            obj.bindBizToGroup.params['chat_group_name'] = obj.bindBizToGroup.form.data.chat_group_name
                        }
                    },
                    submitCallback: (obj) => {
                        obj.getGroupTableData(1)
                    },
                    tearCallback: (obj) => {
                        obj.bindBizToGroup.form.data = {
                            id: -1,
                            chat_bot_type: 'xwork',
                            biz_id: '',
                            biz_name: '',
                            chat_group_id: '',
                            chat_group_name: ''
                        }
                        obj.bindBizToGroup.params = {}
                    }
                },
                unBindBizToGroup: {
                    visible: false,
                    msg: '业务解绑成功',
                    loading: false,
                    mockUrl: ``,
                    openCallback: (obj, row) => {
                        obj.unBindBizToGroup.mockUrl = `${AJAX_URL_PREFIX}/api/v1/chat_bind/` + row.chat_group_id + `/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                    },
                    submitCallback: (obj) => {
                        obj.getGroupTableData(1)
                    }
                }
            }
        },
        watch: {
            bizId: function (val) {
                this.init()
            }
        },
        created () {
        },
        mounted () {
            this.$emit('doHeader', false)
            this.init()
        },
        methods: {
            dialogOpen,
            dialogClean,
            dialogConfirm,
            handleTableSelectionChange,
            init () {
                this.groupYW = this
                if (this.bizId !== '' && typeof this.bizId !== 'undefined') {
                    this.getGroupTableData(1)
                }
            },
            async getGroupTableData (page, filter) {
                const params = { 'page': page, 'biz_id': this.bizId }
                if (typeof filter === 'object') {
                    filter.forEach((item) => {
                        params[item.prop] = item.values.map((k) => {
                            return k.id
                        }).join(',')
                    })
                }

                try {
                    this.groupTableData.loading = true
                    const response = await this.$store.dispatch('group/getGroupTableData', params, {})
                    this.groupTableData.raw = response.data.results || []
                    this.groupTableData.data = JSON.parse(JSON.stringify(this.groupTableData.raw))
                    this.groupTableData.pagination.count = response.data.count
                    this.groupTableData.pagination.current = page
                    this.groupTableData.loading = false
                } catch (e) {
                    console.error(e)
                }
            },
            async checkGroupId (val) {
                const response = await this.$store.dispatch('group/getGroupTableData', { 'chat_group_id': val }, {})
                const data = response.data.results || []
                return !(data.length > 0)
            },
            async getBiz () {
                const response = await this.$store.dispatch('bot/getBiz', {}, {})
                this.bizData.data = response.data || []
            },
            handleTablePageChangeAsync (page) {
                this.getGroupTableData(page, this.groupTableData.searchData.query)
            }
        }
    }
</script>

<style>
    @import './index.css';
</style>
