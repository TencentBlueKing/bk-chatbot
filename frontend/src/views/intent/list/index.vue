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
                    <bk-row>
                        <bk-col :span="9">
                            <div class="content">
                                <bk-button theme="primary"
                                    title="新建"
                                    ext-cls="opsbot-button"
                                    @click="openIntentCreate('intentCreate', null)">新建技能</bk-button>
                                <bk-button theme="default"
                                    title="刷新"
                                    class="mr10"
                                    @click="getTableData(1, intentTableData.searchData.query)">刷新</bk-button>
                            </div>
                        </bk-col>
                        <bk-col :span="3">
                            <div class="content">
                                <bk-search-select clearable :show-popover-tag-change="true"
                                    :data="intentTableData.searchData.data"
                                    v-model="intentTableData.searchData.query" :show-condition="false"
                                    @change="getTableData(1, intentTableData.searchData.query)"
                                    @clear="getTableData(1, intentTableData.searchData.query)"></bk-search-select>
                            </div>
                        </bk-col>
                    </bk-row>
                    <bk-row class="mt15">
                        <bk-col :span="12">
                            <bk-table
                                :data="intentTableData.data"
                                size="small"
                                :pagination="intentTableData.pagination"
                                v-bkloading="{ isLoading: intentTableData.loading, theme: 'primary' }"
                                @page-change="handleTablePageChangeAsync"
                                @selection-change="handleTableSelectionChange($event, intentYW, 'intentTableData')">
                                <!--
                                <bk-table-column type="selection" width="60"></bk-table-column>
                                -->
                                <bk-table-column label="技能名称" prop="intent_name">
                                    <template slot-scope="scope">
                                        <bk-button class="mr10" text theme="primary" @click="openIntentCreate('intentCreate', scope.row)">{{ scope.row.intent_name }}</bk-button>
                                    </template>
                                </bk-table-column>
                                <bk-table-column label="可执行人" prop="available_user">
                                    <template slot-scope="scope">
                                        <span>{{scope.row.available_user.join(',')}}</span>
                                    </template>
                                </bk-table-column>
                                <bk-table-column label="可执群" prop="available_group">
                                    <template slot-scope="scope">
                                        <span>{{scope.row.available_group.join(',')}}</span>
                                    </template>
                                </bk-table-column>
                                <bk-table-column label="修改时间" prop="updated_at"></bk-table-column>
                                <bk-table-column label="状态" prop="status"
                                    :filters="intentTableData.filters.statusFilter.tag"
                                    :filter-method="intentTableData.filters.statusFilter.filterMethod">
                                    <template slot-scope="scope">
                                        <bk-switcher
                                            v-model="scope.row.status"
                                            theme="primary"
                                            size="small"
                                            @change="popConfirm('intentUpdateStatus', scope.row)"></bk-switcher>
                                    </template>
                                </bk-table-column>
                                <bk-table-column label="操作" width="150">
                                    <template slot-scope="scope">
                                        <bk-button
                                            class="mr10"
                                            theme="primary"
                                            text
                                            :ref="'intent-' + scope.$index"
                                            @click="openIntentCreate('intentCreate', scope.row)">
                                            编辑</bk-button>
                                        <bk-popconfirm
                                            trigger="click"
                                            :confirm-button-is-text="false"
                                            confirm-text="确定"
                                            cancel-text="取消"
                                            @confirm="dialogConfirm(intentYW, 'intentDelete', '', 'delete')">
                                            <div slot="content">
                                                <div>
                                                    <i class="bk-icon icon-info-circle-shape pr5" style="color: red;"></i>
                                                    确认删除该项技能: {{ scope.row.intent_name }}
                                                </div>
                                            </div>
                                            <bk-button
                                                class="mr10"
                                                theme="primary"
                                                text
                                                @click="dialogOpen(intentYW, 'intentDelete', intentDelete.openCallback(intentYW, scope.row))">删除</bk-button>
                                        </bk-popconfirm>
                                    </template>
                                </bk-table-column>
                            </bk-table>
                        </bk-col>
                    </bk-row>
                </bk-container>
            </div>
        </div>
        <intentCreateSlider
            ref="intentCreateRef"
            @getTableData="getTableData"
            :bot-id="indexId"
            :biz-id="bizId"></intentCreateSlider>
    </div>
</template>

<script>
    import intentCreateSlider from '../create/index.vue'
    import { dialogOpen, dialogClean, dialogConfirm } from '../../../utils/form'
    import { handleTableSelectionChange } from '../../../utils/table'

    export default {
        components: {
            intentCreateSlider
        },
        props: {
            'bizId': {
                type: String
            }
        },
        data () {
            return {
                intentYW: null,
                indexId: -1,
                intentTableData: {
                    pagination: {
                        current: 1,
                        count: 500,
                        'limit-list': [10],
                        limit: 10
                    },
                    intent: [],
                    raw: [],
                    data: [],
                    title: [],
                    loading: false,
                    filters: {
                        statusFilter: {
                            tag: [{ text: '开启', value: '开启' }, { text: '开启', value: '开启' }],
                            filterMethod: this.tagFilterMethod
                        }
                    },
                    multipleSelection: [],
                    searchData: {
                        data: [
                            {
                                name: '名称',
                                id: '1',
                                prop: 'intent_name',
                                multiable: true,
                                children: []
                            },
                            {
                                name: '创建人',
                                id: '2',
                                prop: 'create_by',
                                multiable: true,
                                children: []
                            }
                        ],
                        query: '',
                        result: []
                    }
                },
                searchData: {
                    data: [
                        {
                            name: '名称',
                            id: '1',
                            prop: 'intent_name',
                            multiable: true,
                            children: []
                        },
                        {
                            name: '创建人',
                            id: '2',
                            prop: 'create_by',
                            multiable: true,
                            children: []
                        }
                    ],
                    query: '',
                    result: []
                },
                intentDelete: {
                    visible: false,
                    msg: '技能删除成功',
                    loading: false,
                    method: 'delete',
                    mockUrl: ``,
                    openCallback: (obj, row) => {
                        obj.intentDelete.mockUrl = `${AJAX_URL_PREFIX}/api/v1/` + obj.bizId + `/intent/` + row.id + `/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                    },
                    submitCallback: (obj) => {
                        obj.getTableData(1)
                    }
                },
                intentUpdateStatus: {
                    visible: false,
                    msg: '操作成功',
                    loading: false,
                    method: 'patch',
                    mockUrl: ``,
                    params: {},
                    openCallback: (obj, row) => {
                        obj.intentUpdateStatus.params = { status: row.status }
                        obj.intentUpdateStatus.mockUrl = `${AJAX_URL_PREFIX}/api/v1/` + obj.bizId + `/intent/` + row.id + `/?${AJAX_MOCK_PARAM}=intent&invoke=common`
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
            this.$emit('doHeader', false, '技能创建')
            this.init()
        },
        methods: {
            handleTableSelectionChange,
            dialogOpen,
            dialogClean,
            dialogConfirm,
            init () {
                this.intentYW = this
                if (this.bizId !== '' && typeof this.bizId !== 'undefined') {
                    this.getTableData(1)
                }
            },
            handleTablePageChangeAsync (page) {
                this.getTableData(page, this.intentTableData.searchData.query)
            },
            tagFilterMethod (value, row, column) {
                const property = column.property
                return row[property] === value
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
                    this.intentTableData.loading = true
                    const response = await this.$store.dispatch('intent/getIntentList', params, {})
                    this.intentTableData.raw = response.data.results || []
                    this.intentTableData.data = JSON.parse(JSON.stringify(this.intentTableData.raw))
                    this.intentTableData.pagination.count = response.data.count
                    this.intentTableData.pagination.current = page
                    this.intentTableData.loading = false
                } catch (e) {
                    console.error(e)
                }
            },
            openIntentCreate (dialogName, obj) {
                this.$refs.intentCreateRef.dialogOpen(dialogName, null, obj)
            },
            popConfirm (popName, row, tag = '') {
                this[popName].openCallback(this.intentYW, row)
                this.dialogConfirm(this.intentYW, 'intentUpdateStatus', '', 'patch')
            }
        }
    }
</script>

<style>
    @import './index.css';
</style>
