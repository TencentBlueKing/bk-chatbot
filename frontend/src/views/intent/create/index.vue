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
        <bk-sideslider
            :is-show.sync="intentCreate.visible"
            :quick-close="true"
            @hidden="dialogClean('intentCreate')"
            ext-cls="opsbot-intent-slider"
            width="800">
            <div slot="header">
                <bk-container :col="12">
                    <bk-row>
                        <bk-col :span="9">
                            <span>技能创建</span>
                        </bk-col>
                        <bk-col :span="3" :class="[botData.isShowBot]">
                            <bk-select v-model="botData.botId"
                                searchable
                                ext-cls="opsbot-create-select"
                                :disabled="botData.disable">
                                <bk-option v-for="option in botData.data"
                                    :key="option.id"
                                    :id="option.id"
                                    :name="option.bot_name">
                                </bk-option>
                            </bk-select>
                        </bk-col>
                    </bk-row>
                </bk-container>
            </div>
            <div slot="content">
                <div class="wrapper">
                    <bk-container :col="12" :gutter="4" ext-cls="opsbot-slider-container">
                        <bk-row>
                            <bk-col :span="12">
                                <bk-collapse v-model="intentCreate.activeTaskMenu" class="opsbot-slider-collapse">
                                    <bk-collapse-item name="1">
                                        任务信息
                                        <div slot="content">
                                            <bk-form :label-width="100"
                                                :model="intentCreate.taskForm"
                                                :rules="intentCreate.taskRules"
                                                ref="taskFormRef">
                                                <bk-form-item label="任务类型" :required="true" property="taskType">
                                                    <bk-select v-model="intentCreate.taskForm.taskType" searchable @select="handleTaskTypeChange">
                                                        <bk-option v-for="option in taskTypeList"
                                                            :disabled="option.enable"
                                                            :key="option.id"
                                                            :id="option.id"
                                                            :name="option.name">
                                                        </bk-option>
                                                    </bk-select>
                                                </bk-form-item>
                                                <bk-form-item label="任务名称" :required="true" property="taskId">
                                                    <bk-row>
                                                        <bk-col :span="10">
                                                            <bk-select
                                                                v-model="intentCreate.taskForm.taskId"
                                                                searchable
                                                                @toggle="getTaskList"
                                                                @selected="getTaskDetail"
                                                                :loading="taskList.loading">
                                                                <bk-option v-for="option in taskList.data"
                                                                    :key="option.id"
                                                                    :id="option.id"
                                                                    :name="option.name">
                                                                </bk-option>
                                                            </bk-select>
                                                        </bk-col>
                                                        <bk-col :span="1">
                                                            <bk-button title="toggle-lock"
                                                                icon="icon-refresh"
                                                                @click="getTaskDetail(intentCreate.taskForm.taskId, -1)" text></bk-button>
                                                        </bk-col>
                                                    </bk-row>
                                                </bk-form-item>
                                                <bk-form-item label="任务分组" property="taskGroup" v-if="intentCreate.taskForm.taskType === 'sops' && intentCreate.taskForm.taskId !== ''">
                                                    <bk-select
                                                        v-model="intentCreate.taskForm.taskGroup"
                                                        searchable
                                                        multiple
                                                        display-tag
                                                        @toggle="getSopsSchemes"
                                                        @selected="handleSopsSchemesSelect"
                                                        :loading="sopsSchemes.loading">
                                                        <bk-option v-for="option in sopsSchemes.data"
                                                            :key="option.id"
                                                            :id="option.id"
                                                            :name="option.name">
                                                        </bk-option>
                                                    </bk-select>
                                                </bk-form-item>
                                                <bk-form-item label="任务参数" property="taskParams" desc="你可以在这里定义技能执行所需要的参数。例如将“qa90 {versionNum} {GroupID}”填写到对应的步骤处">
                                                    <bk-table
                                                        :data="taskParamsTable.data"
                                                        size="small"
                                                        max-height="400"
                                                        ext-cls="opsbot-slider-table"
                                                        :pagination="taskParamsTable.pagination"
                                                        :header-cell-style="{ background: '#fff' }"
                                                        v-bkloading="{ isLoading: taskParamsTable.loading, theme: 'primary' }"
                                                        ref="taskParamsTableRef"
                                                        @page-change="handlePoolPageChange"
                                                        @page-limit-change="handlePoolPageLimitChange"
                                                        @selection-change="handlePoolTableSelectionChange">
                                                        <bk-table-column label="序号" prop="priority" width="60"></bk-table-column>
                                                        <bk-table-column label="参数名" prop="name" sortable></bk-table-column>
                                                        <bk-table-column label="正则" prop="pattern"></bk-table-column>
                                                        <bk-table-column label="提示语" prop="prompt"></bk-table-column>
                                                        <bk-table-column label="操作" width="60">
                                                            <template slot-scope="scope">
                                                                <bk-popover class="dot-menu" placement="bottom-start" theme="dot-menu light" trigger="click" :arrow="false" offset="15" :distance="0">
                                                                    <span class="dot-menu-trigger"></span>
                                                                    <ul class="dot-menu-list" slot="content">
                                                                        <li class="dot-menu-item" @click="dialogOpen('taskParamsConfig', scope.row)">修改</li>
                                                                        <li class="dot-menu-item" @click="deleteParamItem(scope.$index)">删除</li>
                                                                    </ul>
                                                                </bk-popover>
                                                            </template>
                                                        </bk-table-column>
                                                    </bk-table>
                                                </bk-form-item>
                                            </bk-form>
                                        </div>
                                    </bk-collapse-item>
                                </bk-collapse>
                            </bk-col>
                        </bk-row>
                        <bk-row>
                            <bk-col :span="12">
                                <bk-collapse v-model="intentCreate.activeBasicMenu" class="opsbot-slider-collapse">
                                    <bk-collapse-item name="1">
                                        技能参数
                                        <div slot="content">
                                            <bk-form :label-width="100"
                                                :model="intentCreate.intentForm"
                                                :rules="intentCreate.intentRules"
                                                ref="intentFormRef">
                                                <bk-form-item label="技能名称" :required="true" property="intentName">
                                                    <bk-input v-model="intentCreate.intentForm.intentName" placeholder="请输入技能名称" :disabled="!(intent === null)"></bk-input>
                                                </bk-form-item>
                                                <bk-form-item label="语料" :required="true" property="utterance" desc="例如你有一个测试服部署的作业，那你可以添加这样一些语料：“测试服部署”、“QA服部署”等等，回车确认输入完成，多个黏贴;分隔">
                                                    <bk-tag-input
                                                        v-model="intentCreate.intentForm.utterance"
                                                        placeholder="请输入语料"
                                                        :list="list"
                                                        :allow-create="true"
                                                        :has-delete-icon="true"
                                                        :paste-fn="pasteUtteranceFn">
                                                    </bk-tag-input>
                                                </bk-form-item>
                                                <bk-form-item label="发起人" :required="true" property="authorityUsername" desc="发起人必须在群里，回车确认输入完成">
                                                    <bk-tag-input
                                                        v-model="intentCreate.intentForm.authorityUsername"
                                                        placeholder="请输入语料"
                                                        :list="list"
                                                        :allow-create="true"
                                                        :has-delete-icon="true"
                                                        :paste-fn="pasteUsernameFn">
                                                    </bk-tag-input>
                                                </bk-form-item>
                                                <!--
                                                <bk-form-item label="发起群" :required="true" property="authorityGroup"
                                                    desc="在群中@opsbot '查看企业微信ID' 即可获取到企业微信群ID, 在业务群完成群绑定">
                                                    <bk-row>
                                                        <bk-col :span="10">
                                                            <bk-select
                                                                searchable
                                                                multiple
                                                                display-tag
                                                                placeholder="请选择群ID"
                                                                v-model="intentCreate.intentForm.authorityGroup">
                                                                <bk-option v-for="item in groupSummary" :key="item.id" :id="item.id" :name="item.name">
                                                                </bk-option>
                                                                <div slot="extension" @click="goGroupBind" style="cursor: pointer;">
                                                                    <i class="bk-icon icon-plus-circle"></i>新增
                                                                </div>
                                                            </bk-select>
                                                        </bk-col>
                                                        <bk-col :span="1">
                                                            <bk-button title="toggle-lock"
                                                                icon="icon-refresh"
                                                                @click="getGroupSummary()" text></bk-button>
                                                        </bk-col>
                                                    </bk-row>
                                                </bk-form-item>
                                                -->
                                                <bk-form-item label="执行确认" property="doubleCommit" desc="任务执行需要经过确认后才会被执行">
                                                    <bk-switcher v-model="intentCreate.intentForm.doubleCommit" theme="primary"></bk-switcher>
                                                </bk-form-item>
                                            </bk-form>
                                        </div>
                                    </bk-collapse-item>
                                </bk-collapse>
                            </bk-col>
                        </bk-row>
                    </bk-container>
                </div>
            </div>
            <div slot="footer">
                <bk-button style="margin-left: 30px;" theme="primary" :loading="intentCreate.loading"
                    @click="dialogValidate('intentCreate', 'intentCreateRef')">确定
                </bk-button>
                <bk-button theme="default" @click="intentCreate.visible = false">关闭</bk-button>
            </div>
        </bk-sideslider>
        <bk-dialog
            v-model="taskParamsConfig.visible"
            theme="primary"
            header-position="left"
            title="参数配置"
            :auto-close="false"
            :loading="taskParamsConfig.loading"
            @confirm="dialogValidate('taskParamsConfig', 'taskParamsConfigRef')"
            @cancel="dialogCancel('taskParamsConfig')"
            @after-leave="dialogClean('taskParamsConfig')">
            <bk-form :label-width="200" form-type="vertical" ref="taskParamsConfigRef"
                :model="taskParamsConfig.form.data"
                :rules="taskParamsConfig.form.rules">
                <bk-form-item label="参数名称" :required="true" property="name">
                    <bk-input v-model="taskParamsConfig.form.data.name" maxlength="50" disabled></bk-input>
                </bk-form-item>
                <bk-form-item label="正则" :required="true" property="pattern">
                    <bk-input v-model="taskParamsConfig.form.data.pattern"></bk-input>
                </bk-form-item>
                <bk-form-item label="提示语" :required="true" property="prompt">
                    <bk-input v-model="taskParamsConfig.form.data.prompt"></bk-input>
                </bk-form-item>
                <bk-form-item label="正则测试">
                    <bk-input v-model="taskParamsConfig.test" placeholder="请输入验证参数">
                        <template slot="append">
                            <bk-button theme="primary" style="border: none; height: 30px; border-radius: 0;" @click="testPattern()">测试</bk-button>
                        </template>
                    </bk-input>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>

<script>
    import http from '@/api'
    import { submitRequest } from '../../../utils/form'
    import { goPage } from '../../../utils/stdlib'
    import { messageError, messageSuccess } from '@/common/bkmagic'

    export default {
        components: {
        },
        props: {
            'botId': {
                type: String
            },
            'bizId': {
                type: String
            }
        },
        data () {
            return {
                intent: null,
                botData: {
                    botId: -1,
                    botName: '',
                    isShowBot: 'display: none',
                    visible: true,
                    disable: false,
                    data: []
                },
                groupSummary: [],
                intentCreate: {
                    visible: false,
                    msg: '技能创建成功',
                    activeTaskMenu: '1',
                    activeBasicMenu: '1',
                    loading: false,
                    method: 'post',
                    taskForm: {
                        taskType: 'job',
                        taskName: '',
                        taskId: '',
                        taskGroup: [],
                        taskActivities: [],
                        taskParams: []
                    },
                    taskRules: {
                        taskType: [
                            { required: true, message: '请选择任务类型', trigger: 'change' }
                        ],
                        taskId: [
                            { required: true, message: '请选择任务名', trigger: 'change' }
                        ]
                    },
                    intentForm: {
                        intentName: '',
                        utterance: [],
                        authorityUsername: [],
                        authorityGroup: [],
                        doubleCommit: false
                    },
                    intentRules: {
                        intentName: [
                            { required: true, message: '请填写技能名称', trigger: 'blur' }
                        ],
                        utterance: [
                            { message: '请输入语料', validator: this.validateListParam, trigger: 'blur' }
                        ],
                        authorityUsername: [
                            { message: '请输入发起人', validator: this.validateListParam, trigger: 'blur' }
                        ],
                        authorityGroup: [
                            { message: '请输入发起群', validator: this.validateListParam, trigger: 'blur' }
                        ]
                    }
                },
                taskTypeList: [
                    {
                        id: 'job',
                        name: '作业平台',
                        enable: false
                    },
                    {
                        id: 'sops',
                        name: '标准运维',
                        enable: false
                    },
                    {
                        id: 'devops',
                        name: '蓝盾',
                        enable: true
                    }
                ],
                taskList: {
                    source: [],
                    data: [],
                    map: {},
                    detail: {},
                    loading: false
                },
                sopsSchemes: {
                    source: [],
                    data: [],
                    map: {},
                    detail: {},
                    loading: false
                },
                taskParamsTable: {
                    pagination: {
                        current: 1,
                        count: 200,
                        'limit-list': [5, 10],
                        limit: 5
                    },
                    params: [],
                    data: [],
                    title: [],
                    multipleSelection: [],
                    loading: false,
                    query: ''
                },
                taskParamsConfig: {
                    rowRef: null,
                    visible: false,
                    loading: false,
                    msg: '参数配置成功',
                    test: '',
                    form: {
                        data: {
                            name: '',
                            pattern: '',
                            prompt: ''
                        },
                        rules: {
                            name: [
                                { required: true, message: '请输入参数名称', trigger: 'blur' }
                            ],
                            pattern: [
                                { required: true, message: '请输入匹配正则', trigger: 'blur' }
                            ],
                            prompt: [
                                { required: true, message: '请输入提示语', trigger: 'blur' }
                            ]
                        }
                    }
                }
            }
        },
        created () {

        },
        methods: {
            goPage,
            goGroupBind () {
                this.goPage(this, '/group/bind', true)
            },
            pasteUtteranceFn (v) {
                const target = v.split(';')
                this.intentCreate.intentForm.utterance = this.intentCreate.intentForm.utterance.concat(target)
            },
            pasteUsernameFn (v) {
                const target = v.split(';')
                this.intentCreate.intentForm.authorityUsername = this.intentCreate.intentForm.authorityUsername.concat(target)
            },
            handlePoolPageChange (page) {
                this.taskParamsTable.pagination.current = page
                this.taskParamsTable.data = this.taskParamsTable.params.slice((page - 1) * this.taskParamsTable.pagination.limit, page * this.taskParamsTable.pagination.limit)
            },
            handlePoolPageLimitChange (limit) {
                this.taskParamsTable.pagination.current = 1
                this.taskParamsTable.data = this.taskParamsTable.params.slice(0, limit)
            },
            handlePoolTableSelectionChange (selection) {
                this.taskParamsTable.multipleSelection = selection
            },
            async validateListParam (value) {
                if (value.length === 0) {
                    return false
                }
                return true
            },
            dialogOpen (dialogName, row, obj) {
                // add form val
                if (dialogName === 'taskParamsConfig') {
                    this.taskParamsConfig.form.data.name = row.name
                    this.taskParamsConfig.form.data.pattern = row.pattern
                    this.taskParamsConfig.form.data.prompt = row.prompt
                    this.rowRef = row
                } else if (dialogName === 'intentCreate') {
                    this.botData.botId = this.botId
                    this.getBotTableList()
                    this.botData.isShowBot = 'display: block'
                    this.botData.disable = true

                    if (obj) {
                        this.intent = obj
                        this.getIntentDetail(obj)
                    } else {
                        this.intent = null
                    }
                }

                this.getGroupSummary()

                this[dialogName].visible = true
            },
            dialogValidate (dialogName, formRef) {
                if (dialogName === 'intentCreate') {
                    Promise.all([
                        this.$refs['taskFormRef'].validate(),
                        this.$refs['intentFormRef'].validate()
                    ]).then(values => {
                        if (values.indexOf(false) === -1) {
                            this.dialogConfirm(dialogName)
                        }
                    })
                } else if (formRef === '') {
                    this.dialogConfirm(dialogName)
                } else {
                    this.$refs[formRef].validate().then(validator => {
                        this.dialogConfirm(dialogName)
                    }, validator => {
                        console.log('failed')
                    })
                }
            },
            dialogConfirm (dialogName) {
                let params = {}
                let mockUrl = ''
                let callback = null

                if (dialogName === 'intentCreate') {
                    callback = (obj) => {
                        obj.$bkMessage({
                            theme: 'success',
                            message: obj[dialogName].msg
                        })
                        obj.$emit('getTableData', 1)
                    }

                    params = {
                        biz_id: this.bizId,
                        id: -1,
                        index_id: this.botId,
                        intent_name: this.intentCreate.intentForm.intentName,
                        available_user: this.intentCreate.intentForm.authorityUsername,
                        available_group: this.intentCreate.intentForm.authorityGroup,
                        utterances: this.intentCreate.intentForm.utterance,
                        status: true,
                        is_commit: this.intentCreate.intentForm.doubleCommit,
                        platform: this.intentCreate.taskForm.taskType,
                        task_id: this.intentCreate.taskForm.taskId,
                        activities: this.intentCreate.taskForm.taskActivities,
                        slots: this.taskParamsTable.params,
                        source: this.taskList.detail
                    }

                    // mockUrl = `${AJAX_URL_PREFIX}/api/v1/` + this.bizId + `/intent/create_intent/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                    mockUrl = `${AJAX_URL_PREFIX}/api/v1/` + this.bizId + `/intent/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                    if (this.intent) {
                        this.intentCreate.method = 'patch'
                        params['id'] = this.intent.id
                        mockUrl = `${AJAX_URL_PREFIX}/api/v1/` + this.bizId + `/intent/` + this.intent.id + `/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                    } else {
                        this.intentCreate.method = 'post'
                        mockUrl = `${AJAX_URL_PREFIX}/api/v1/` + this.bizId + `/intent/?${AJAX_MOCK_PARAM}=intent&invoke=common`
                    }
                } else if (dialogName === 'taskParamsConfig') {
                    this.rowRef.name = this.taskParamsConfig.form.data.name
                    this.rowRef.pattern = this.taskParamsConfig.form.data.pattern
                    this.rowRef.prompt = this.taskParamsConfig.form.data.prompt
                    this[dialogName].visible = false
                    return
                }

                submitRequest(mockUrl, params, dialogName, this, callback, this.intentCreate.method)
            },
            dialogCancel (dialogName) {

            },
            dialogClean (dialogName) {
                if (dialogName === 'intentCreate') {
                    this.intentCreate.taskForm = {
                        taskType: 'job',
                        taskName: '',
                        taskId: '',
                        taskParams: []
                    }

                    this.intentCreate.intentForm = {
                        intentName: '',
                        utterance: [],
                        authorityUsername: [],
                        authorityGroup: [],
                        doubleCommit: false
                    }

                    this.taskParamsTable.data = []
                    this.taskParamsTable.params = []
                    try {
                        this.$refs['intentFormRef'].clearError()
                        this.$refs['taskFormRef'].clearError()
                    } catch (e) {
                        console.log('...')
                    }
                } else if (dialogName === 'taskParamsConfig') {
                    this.$refs['taskParamsConfigRef'].clearError()
                }
            },
            handleTaskTypeChange (n, o) {
                this.intentCreate.taskForm.taskId = ''
                this.taskList.data = []
                this.taskParamsTable.data = []
                this.taskParamsTable.params = []
            },
            async getBotTableList () {
                // 分页可能会查不到
                const response = await this.$store.dispatch('bot/getBotTableData', { 'bizId': this.bizId, 'data': { 'biz_id': this.bizId } }, {})
                this.botData.data = response.data.results || []
                this.botData.botId = this.botId
            },
            async getIntentDetail (obj) {
                this.taskParamsTable.loading = true
                this.intentCreate.intentForm.intentName = obj.intent_name
                this.intentCreate.intentForm.authorityGroup = obj.available_group
                this.intentCreate.intentForm.authorityUsername = obj.available_user
                this.intentCreate.intentForm.doubleCommit = obj.is_commit
                let response = await this.$store.dispatch('intent/getUtteranceList', { 'bizId': this.bizId, 'data': { 'index_id': obj.id } }, {})
                const utterance = response.data || []
                this.intentCreate.intentForm.utterance = utterance.length > 0 ? utterance[0].content : []

                response = await this.$store.dispatch('intent/getDBTaskList', { 'bizId': this.bizId, 'data': { 'index_id': obj.id } }, {})
                let taskParams = response.data || []
                taskParams = taskParams.length > 0 ? taskParams[0] : {}
                this.intentCreate.taskForm.taskType = taskParams.platform
                this.intentCreate.taskForm.taskId = parseInt(taskParams.task_id)
                this.intentCreate.taskForm.taskActivities = taskParams.activities
                this.intentCreate.taskForm.taskGroup = taskParams.activities.map((item) => {
                    return item.id
                })
                this.taskList.detail = taskParams.source
                this.taskParamsTable.params = taskParams['slots']
                this.taskParamsTable.pagination.count = this.taskParamsTable.params.length
                this.taskParamsTable.data = this.taskParamsTable.params.slice(0, this.taskParamsTable.pagination.limit)
                this.taskParamsTable.loading = false
                this.getTaskList(true)
            },
            async getGroupSummary () {
                const response = await this.$store.dispatch('group/getGroupSummary', { 'biz_id': this.bizId, 'id_deleted': false }, {})
                this.groupSummary = response.data.map((e) => {
                    return { 'id': e.chat_index_id, 'name': e.chat_group_name }
                })
            },
            getTaskList (status) {
                if (!status) {
                    this.taskList.data = []
                    return
                }

                const params = {}
                let mockUrl = ''

                if (this.intentCreate.taskForm.taskType === 'job') {
                    mockUrl = `${AJAX_URL_PREFIX}/api/v1/task/` + this.bizId + `/describe_jobs/?${AJAX_MOCK_PARAM}=intent&invoke=jobListV3`
                } else if (this.intentCreate.taskForm.taskType === 'sops') {
                    mockUrl = `${AJAX_URL_PREFIX}/api/v1/task/` + this.bizId + `/describe_sopss/?${AJAX_MOCK_PARAM}=intent&invoke=sopsList`
                }

                this.taskList.loading = true
                http.post(mockUrl, params, {}).then(response => {
                    this.taskList.source = response.data || []
                    this.taskList.data = this.taskList.source
                    this.taskList.loading = false
                })
            },
            getTaskDetail (n, o) {
                if (n === '' || typeof n === 'undefined') {
                    return
                }
                const params = { id: n }
                let mockUrl = ''

                if (this.intentCreate.taskForm.taskType === 'job') {
                    mockUrl = `${AJAX_URL_PREFIX}/api/v1/task/` + this.bizId + `/describe_job/?${AJAX_MOCK_PARAM}=intent&invoke=jobDetailV3`
                } else if (this.intentCreate.taskForm.taskType === 'sops') {
                    mockUrl = `${AJAX_URL_PREFIX}/api/v1/task/` + this.bizId + `/describe_sops/?${AJAX_MOCK_PARAM}=intent&invoke=sopsDetail`
                    if (this.intentCreate.taskForm.taskId !== '') {
                        this.getSopsSchemes()
                    }
                }

                this.taskParamsTable.loading = true
                http.post(mockUrl, params, {}).then(response => {
                    this.taskParamsTable.data = []
                    this.taskParamsTable.params = []
                    const tmp = response.data || {}
                    if ('global_var_list' in tmp) {
                        this.taskParamsTable.params = tmp['global_var_list'].map(function (item, index, input) {
                            return {
                                priority: index + 1,
                                id: item['id'],
                                name: item['name'],
                                pattern: '.*',
                                prompt: '请输入' + item['name'],
                                type: item['type'],
                                value: item['value']
                            }
                        })
                    } else if ('pipeline_tree' in tmp && 'constants' in tmp['pipeline_tree']) {
                        let index = 1
                        for (const item in tmp['pipeline_tree']['constants']) {
                            if (tmp['pipeline_tree']['constants'][item]['show_type'] === 'show') {
                                this.taskParamsTable.params.push({
                                    id: item,
                                    priority: index,
                                    name: tmp['pipeline_tree']['constants'][item]['name'],
                                    pattern: tmp['pipeline_tree']['constants'][item]['validation'],
                                    prompt: '请输入' + tmp['pipeline_tree']['constants'][item]['name']
                                })
                                index++
                            }
                        }
                    }
                    this.taskList.detail = tmp
                    this.taskParamsTable.pagination.count = this.taskParamsTable.params.length
                    this.taskParamsTable.data = this.taskParamsTable.params.slice(0, this.taskParamsTable.pagination.limit)
                    this.taskParamsTable.loading = false
                })
            },
            async getSopsSchemes () {
                this.sopsSchemes.loading = true
                const response = await this.$store.dispatch('intent/getSopsSchemes', { 'bizId': this.bizId, 'id': this.intentCreate.taskForm.taskId }, {})
                this.sopsSchemes.data = response.data || []
                this.sopsSchemes.data.forEach((item) => {
                    this.sopsSchemes.map[item.id] = item
                })
                this.sopsSchemes.loading = false
            },
            handleSopsSchemesSelect (n, o) {
                // const allTaskNodes = Object.keys(this.taskList.detail.pipeline_tree.activities)
                // const excludeTaskNodes = n.flatMap((id) => {
                //     return this.sopsSchemes.map[id]
                // })
                // this.intentCreate.taskForm.taskActivities = allTaskNodes.filter((v) => {
                //     return excludeTaskNodes.indexOf(v) === -1
                // })
                this.intentCreate.taskForm.taskActivities = n.map((id) => {
                    return this.sopsSchemes.map[id]
                })
            },
            deleteParamItem (index) {
                this.taskParamsTable.params.splice(index, 1)
                this.taskParamsTable.pagination.count = this.taskParamsTable.params.length
                this.taskParamsTable.data = this.taskParamsTable.params.slice(0, this.taskParamsTable.pagination.limit)
            },
            testPattern () {
                const regex = new RegExp(this.taskParamsConfig.form.data.pattern)
                const result = regex.exec(this.taskParamsConfig.test)
                if (result) {
                    messageSuccess(result[0])
                } else {
                    messageError('正则匹配失败')
                }
            }
        }
    }
</script>

<style>
    @import './index.css';
</style>
