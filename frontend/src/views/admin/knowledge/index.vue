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
    <div>
        <div class="main-content" v-if="isAuth === true">
            <div class="app-container">
            </div>
            <div class="app-content">
                <div class="wrapper">
                    <div class="task-layout">
                        <div :class="['layout-left', isOpen]">
                            <div class="scroll-faker-wrapper">
                                <div class="scroll-faker-content">
                                    <div class="job-tag-wrapper">
                                        <div
                                            v-for="item in baseNameTable.data"
                                            :key="item.id"
                                            @click="handleBaseNameSelect(item)"
                                            :class="item.class">
                                            <i class="tag-flag bk-icon icon-data"></i>
                                            <div class="tag-name">
                                                <div class="name-text" tabindex="0">{{ item.faq_name }}</div>
                                            </div>
                                            <div class="tag-num-box"><span class="tag-num">{{ item.num }}</span></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="layout-right">
                            <div class="toggle-button">
                                <bk-button theme="default" text @click="switchTab">
                                    <i :class="['bk-icon', openAngle]"></i>
                                </bk-button>
                            </div>
                            <bk-container :col="12" :gutter="4">
                                <bk-row>
                                    <bk-col :span="7">
                                        <div class="content">
                                            <bk-button title="primary" :text="true" :hover-theme="'primary'" class="mr10" @click="dialogOpen('createQA')">
                                                新建
                                            </bk-button>
                                            <bk-button title="warning"
                                                :hover-theme="'primary'"
                                                class="mr10"
                                                @click="dialogOpen('deleteQA')"
                                                :disabled="multipleSelection.length === 0 ? true : false">
                                                删除
                                            </bk-button>
                                        </div>
                                    </bk-col>
                                    <bk-col :span="5">
                                        <div class="content">
                                            <bk-search-select clearable :show-popover-tag-change="true"
                                                :data="searchData.data"
                                                v-model="searchData.query" :show-condition="false"
                                                @change="searchResult"
                                                @clear="getQATableData(selectDB, selectCollection)"></bk-search-select>
                                        </div>
                                    </bk-col>
                                </bk-row>
                                <bk-row>
                                    <bk-col :span="12">
                                        <bk-table style="margin-top: 15px;" :data="knowledgeBaseTable.data"
                                            size="small"
                                            max-height="666"
                                            :pagination="knowledgeBaseTable.pagination"
                                            v-bkloading="{ isLoading: knowledgeBaseTable.loading, theme: 'primary' }"
                                            @page-change="handlePageChange"
                                            @page-limit-change="handlePageLimitChange"
                                            @selection-change="handleTableSelectionChange">
                                            <bk-table-column type="selection" width="60"></bk-table-column>
                                            <bk-table-column label="ID" prop="_id"></bk-table-column>
                                            <bk-table-column label="问题" prop="question"></bk-table-column>
                                            <bk-table-column label="答案" prop="solution"></bk-table-column>
                                            <bk-table-column label="创建人" prop="username" width="100"></bk-table-column>
                                            <bk-table-column label="操作" width="150">
                                                <template slot-scope="scope">
                                                    <bk-button class="mr10" theme="primary" text @click="dialogOpen('createQA', scope.row)">编辑</bk-button>
                                                </template>
                                            </bk-table-column>
                                        </bk-table>
                                    </bk-col>
                                </bk-row>
                            </bk-container>
                        </div>
                    </div>
                </div>
            </div>
            <bk-dialog v-model="createQA.visible" theme="primary"
                width="600"
                header-position="left"
                :title="createQA.title"
                :auto-close="false"
                :loading="createQA.loading"
                @confirm="dialogValidate('createQA', 'createQARef')"
                @after-leave="dialogClean('createQARef')">
                <bk-form :label-width="100" ref="createQARef"
                    :model="createQA.form.data"
                    :rules="createQA.form.rules">
                    <bk-form-item
                        label="问题"
                        v-for="(question, index) in createQA.form.data.questions"
                        :required="true"
                        :rules="createQA.form.rules.question"
                        :icon-offset="95"
                        :property="'questions.' + index + '.value'"
                        :key="index">
                        <bk-input v-model="question.value" placeholder="请输入问题">
                            <template slot="append">
                                <bk-button icon="plus"
                                    theme="primary"
                                    style="border: none; height: 30px; border-radius: 0;"
                                    @click="addQuestion">新增</bk-button>
                            </template>
                        </bk-input>
                    </bk-form-item>
                    <bk-form-item label="解决方案" :required="true" property="solution">
                        <bk-input v-model="createQA.form.data.solution"
                            placeholder="请输入解决方案"></bk-input>
                    </bk-form-item>
                </bk-form>
            </bk-dialog>
            <bk-dialog v-model="deleteQA.visible" theme="primary"
                width="500"
                header-position="left"
                :title="deleteQA.title"
                :auto-close="false"
                :loading="deleteQA.loading"
                @confirm="dialogValidate('deleteQA', '')"
                @after-leave="dialogClean('deleteQARef')">
                确认删除：<p>{{ deleteQA.tip }}</p>
            </bk-dialog>
        </div>
        <bk-exception class="exception-wrap-item" type="403" v-else>
            <span>无查看权限</span>
            <div class="text-subtitle">你没有相应业务的访问权限，请前往申请相关业务权限</div>
            <div class="text-wrap">
                <span class="text-btn">找小明</span>
            </div>
        </bk-exception>
    </div>
</template>

<script>
    import http from '@/api'
    import queryString from 'query-string'
    import { submitRequest } from '../../../utils/form'

    export default {
        components: {
        },
        data () {
            return {
                isAuth: true,
                selectDB: '',
                selectCollection: '',
                isOpen: 'is-expand',
                openAngle: 'icon-angle-left',
                baseNameTable: {
                    data: [],
                    loading: false
                },
                knowledgeBaseTable: {
                    pagination: {
                        current: 1,
                        count: 500,
                        'limit-list': [5, 10, 50, 100],
                        limit: 10
                    },
                    base: [],
                    data: [],
                    title: [],
                    loading: false
                },
                searchData: {
                    data: [
                        {
                            name: '创建人',
                            id: '1',
                            prop: 'username',
                            multiable: true,
                            children: []
                        },
                        {
                            name: '问题',
                            id: '2',
                            prop: 'question',
                            multiable: true,
                            children: []
                        },
                        {
                            name: '答案',
                            id: '3',
                            prop: 'solution',
                            multiable: true,
                            children: []
                        }
                    ],
                    query: '',
                    result: []
                },
                multipleSelection: [],
                deleteQA: {
                    visible: false,
                    msg: 'QA删除成功',
                    loading: false,
                    title: 'QA删除',
                    data: [],
                    tip: ''
                },
                createQA: {
                    visible: false,
                    loading: false,
                    msg: 'QA创建成功',
                    title: 'QA创建',
                    form: {
                        data: {
                            id: '',
                            questions: [
                                { value: '' }
                            ],
                            solution: ''
                        },
                        rules: {
                            solution: [
                                { required: true, message: '请输问题答案', trigger: 'blur' }
                            ],
                            question: [
                                { required: true, message: '请输问题', trigger: 'blur' }
                            ]
                        }
                    }
                }
            }
        },
        mounted () {
            this.$emit('doHeader', false)
            this.getBaseNameTableData()
        },
        methods: {
            switchTab () {
                if (this.isOpen === 'is-expand') {
                    this.isOpen = 'is-collapse'
                    this.openAngle = 'icon-angle-right'
                } else {
                    this.isOpen = 'is-expand'
                    this.openAngle = 'icon-angle-left'
                }
            },
            handlePageChange (page) {
                this.knowledgeBaseTable.pagination.current = page
                this.knowledgeBaseTable.data = this.knowledgeBaseTable.base.slice((page - 1) * this.knowledgeBaseTable.pagination.limit, page * this.knowledgeBaseTable.pagination.limit)
            },
            handlePageLimitChange (limit) {
                this.knowledgeBaseTable.pagination.current = 1
                this.knowledgeBaseTable.data = this.knowledgeBaseTable.base.slice(0, limit)
            },
            handleTableSelectionChange (selection) {
                this.multipleSelection = selection
            },
            handleBaseNameSelect (val) {
                this.baseNameTable.data = this.baseNameTable.data.map(function (item) {
                    item.class = 'task-list-tag-edit display'
                    return item
                })

                val.class = 'task-list-tag-edit display active'
                this.selectDB = val.faq_db
                this.selectCollection = val.faq_collection
                this.getQATableData(val.faq_db, val.faq_collection)
            },
            getBaseNameTableData () {
                const params = {
                    'member__contains': this.$store.state.user.username
                }
                const mockUrl = `${AJAX_URL_PREFIX}/api/v1/faq/?${AJAX_MOCK_PARAM}=intent&invoke=baseList&${queryString.stringify(params)}`
                this.baseNameTable.loading = true
                http.get(mockUrl, params, {}).then(response => {
                    this.baseNameTable.data = response.data.results || []
                    this.baseNameTable.data = this.baseNameTable.data.map(function (item) {
                        item.class = 'task-list-tag-edit display'
                        return item
                    })
                    if (this.baseNameTable.data.length > 0) {
                        this.baseNameTable.data[0].class = 'task-list-tag-edit display active'
                        this.selectDB = this.baseNameTable.data[0].faq_db
                        this.selectCollection = this.baseNameTable.data[0].faq_collection
                        this.getQATableData(this.selectDB, this.selectCollection)
                    }
                    this.baseNameTable.loading = false
                }).catch((e) => {
                    this.isAuth = false
                })
            },
            getQATableData (db, collection) {
                const params = {
                    faq_db: db,
                    faq_collection: collection
                }
                const mockUrl = `${AJAX_URL_PREFIX}/api/v1/faq/describe_qas/?${AJAX_MOCK_PARAM}=intent&invoke=qaList`
                this.knowledgeBaseTable.loading = true
                http.post(mockUrl, params, {}).then(response => {
                    this.knowledgeBaseTable.base = response.data || []
                    this.knowledgeBaseTable.pagination.count = this.knowledgeBaseTable.base.length
                    for (const item in this.searchData.data) {
                        const col = this.searchData.data[item].prop
                        this.searchData.data[item].children = this.knowledgeBaseTable.base.map(function (item, index, input) {
                            return {
                                name: item[col],
                                id: item[col]
                            }
                        })
                    }

                    this.knowledgeBaseTable.data = this.knowledgeBaseTable.base.slice(0, this.knowledgeBaseTable.pagination.limit)
                    this.knowledgeBaseTable.pagination.current = 1
                    this.knowledgeBaseTable.loading = false
                }).catch((e) => {
                    this.isAuth = false
                })
            },
            searchResult () {
                this.searchData.result = []
                for (let i = 0; i < this.knowledgeBaseTable.base.length; i++) {
                    const bot = this.knowledgeBaseTable.base[i]
                    let flag = true
                    for (let j = 0; j < this.searchData.query.length; j++) {
                        const query = this.searchData.query[j]
                        const queryList = query['values'].map(function (item, index, input) {
                            return item['id']
                        })

                        if (queryList.indexOf(bot[query['prop']]) === -1) {
                            flag = false
                            break
                        }
                    }

                    if (flag) {
                        this.searchData.result.push(bot)
                    }
                }

                this.knowledgeBaseTable.pagination.count = this.searchData.result.length
                this.knowledgeBaseTable.data = this.searchData.result.slice(0, this.knowledgeBaseTable.pagination.limit)
                this.knowledgeBaseTable.pagination.current = 1
            },
            dialogOpen (dialogName, row) {
                if (dialogName === 'createQA') {
                    if (typeof row !== 'undefined') {
                        this.createQA.title = 'QA修改'
                        this.createQA.form.data.id = row._id
                        this.createQA.form.data.solution = row.solution
                        this.createQA.form.data.questions[0].value = row.question
                    } else {
                        this.createQA.title = 'QA创建'
                    }
                } else if (dialogName === 'deleteQA') {
                    this.deleteQA.data = this.multipleSelection.map(function (item) {
                        return item['_id']
                    })
                    this.deleteQA.tip = this.deleteQA.data.join(', ')
                }
                this[dialogName].visible = true
            },
            dialogValidate (dialogName, formRef) {
                if (formRef === '') {
                    this.dialogConfirm(dialogName, formRef)
                } else {
                    this.$refs[formRef].validate().then(validator => {
                        this.dialogConfirm(dialogName, formRef)
                    }, validator => {
                        console.log('failed')
                    })
                }
            },
            dialogConfirm (dialogName, formRef) {
                let params = this.createQA.form.data
                let mockUrl = ''
                const callback = (obj) => {
                    obj.$bkMessage({
                        theme: 'success',
                        message: obj[dialogName].msg
                    })
                    obj.getQATableData(obj.selectDB, obj.selectCollection)
                }

                if (dialogName === 'createQA') {
                    params['username'] = this.$store.state.user.username
                    params['faq_db'] = this.selectDB
                    params['faq_collection'] = this.selectCollection
                    if (params.id === '') {
                        mockUrl = `${AJAX_URL_PREFIX}/api/v1/faq/create_qa/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                    } else {
                        mockUrl = `${AJAX_URL_PREFIX}/api/v1/faq/update_qa/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                    }
                } else if (dialogName === 'deleteQA') {
                    params = {
                        ids: this.deleteQA.data,
                        faq_db: this.selectDB,
                        faq_collection: this.selectCollection
                    }
                    mockUrl = `${AJAX_URL_PREFIX}/api/v1/faq/delete_qa/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                }
                submitRequest(mockUrl, params, dialogName, this, callback)
            },
            dialogClean (dialogName) {
                if (dialogName === 'createQARef') {
                    this.createQA.form.data = {
                        questions: [
                            { value: '' }
                        ],
                        solution: '',
                        username: this.$store.state.user.username,
                        id: ''
                    }

                    this.$refs[dialogName].clearError()
                } else if (dialogName === 'deleteQARef') {
                    this.deleteQA.data = []
                    this.deleteQA.tip = ''
                }
            },
            addQuestion () {
                this.createQA.form.data.questions.push({ value: '' })
            }
        }
    }
</script>

<style>
    @import './index.css';
</style>
