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
                <bk-container :col="12" :gutter="30" class="neo-chart">
                    <bk-row>
                        <bk-col :span="3">
                            <bk-card class="opsbot-chart-card" :show-head="false">
                                <br />
                                <span style="font-size: 28px;">机器人数</span>
                                <br />
                                <span style="font-size: 24px;"><bk-animate-number value="1"></bk-animate-number></span>
                            </bk-card>
                        </bk-col>
                        <bk-col :span="3">
                            <bk-card class="opsbot-chart-card" :show-head="false">
                                <br />
                                <span style="font-size: 28px;">技能数</span>
                                <br />
                                <span style="font-size: 24px;"><bk-animate-number :value="intentNum"></bk-animate-number></span>
                            </bk-card>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-card title="知识库" class="opsbot-chart-base">
                                <bk-collapse accordion v-model="qaActiveName">
                                    <bk-collapse-item name="1">
                                        <span><i class="bk-icon icon-question-circle"></i>  什么是BK-ChatBot</span>
                                        <div slot="content" class="f13">
                                            BK-ChatBot 是一款可通过可视化的界面进行任务配置，由聊天终端软件如企业微信应用机器人进行会话交互实现任务执行的蓝鲸 SaaS 产品。                                        </div>
                                    </bk-collapse-item>

                                    <bk-collapse-item name="2">
                                        <span><i class="bk-icon icon-question-circle"></i>  如何玩BK-ChatBot</span>
                                        <div slot="content" class="f13">
                                            <bk-link theme="primary" icon="bk-icon icon-chain" href="https://github.com/TencentBlueKing/bk-chatbot">部署文档</bk-link>
                                        </div>
                                    </bk-collapse-item>
                                </bk-collapse>
                            </bk-card>
                        </bk-col>
                    </bk-row>
                    <bk-row style="margin-top: 20px">
                        <bk-col :span="6">
                            <bk-card title="将以下任务创建为技能" style="height: 300px">
                                <bk-table
                                    :outer-border="false"
                                    :row-border="false"
                                    :data="taskRecordTable.data"
                                    :show-header="false"
                                    size="small"
                                    max-height="200">
                                    <bk-table-column label="平台" prop="platform" width="60"></bk-table-column>
                                    <bk-table-column label="名称" prop="name"></bk-table-column>
                                    <bk-table-column label="日期" prop="end_time">
                                        <template slot-scope="props">
                                            <span>{{ formatDate(new Date(props.row.end_time), 'yyyy-MM-dd hh:mm:ss') }}</span>
                                        </template>
                                    </bk-table-column>
                                    <bk-table-column label="操作" width="150">
                                        <template slot-scope="props">
                                            <bk-button class="mr10" theme="primary" text @click="remove(props.row)" disabled>创建</bk-button>
                                        </template>
                                    </bk-table-column>
                                </bk-table>
                            </bk-card>
                        </bk-col>
                        <bk-col :span="6">
                            <bk-card title="最近执行记录" style="height: 300px; overflow-x: auto">
                                <bk-table
                                    :data="taskExecutionLogTable.data"
                                    :outer-border="false"
                                    :header-border="false"
                                    :show-header="false"
                                    max-height="200">
                                    <bk-table-column label="平台" prop="platform" width="70"></bk-table-column>
                                    <bk-table-column label="技能" prop="intent_name"></bk-table-column>
                                    <bk-table-column label="执行人" prop="sender" width="100"></bk-table-column>
                                    <bk-table-column label="状态" prop="status">
                                        <template slot-scope="props">
                                            <span v-if="props.row.status === '0'" style="color: #c4c6cc">初始状态</span>
                                            <span v-else-if="props.row.status === '1'" style="color: #3a84ff">执行中</span>
                                            <span v-else-if="props.row.status === '2'" style="color: #2dcb56">执行成功</span>
                                            <span v-else-if="props.row.status === '3'" style="color: #ea3636">执行失败</span>
                                            <span v-else-if="props.row.status === '4'" style="color: #c4c6cc">执行暂停</span>
                                            <span v-else-if="props.row.status === '5'" style="color: #ea3636">异常|终止</span>
                                        </template>
                                    </bk-table-column>
                                    <bk-table-column label="开始时间" prop="start_time"></bk-table-column>
                                </bk-table>
                            </bk-card>
                        </bk-col>
                    </bk-row>
                </bk-container>
            </div>
        </div>
    </div>
</template>

<script>
    import { formatDate } from '../../utils/date'

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

                taskRecordTable: {
                    data: [],
                    loading: false
                },
                taskExecutionLogTable: {
                    data: [],
                    loading: false
                },
                qaActiveName: '',
                botNum: 0,
                intentNum: 0
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
            formatDate,
            init () {
                if (this.bizId !== '' && typeof this.bizId !== 'undefined') {
                    const params = {
                        username: this.$store.state.user.username,
                        token: 'inkG6qvWnmu935tnk19vN3f1jhPsybv5',
                        data: {
                            biz_id: Number(this.bizId)
                        }
                    }

                    this.getRecordTableData(params)
                    this.getLogTableData(params)
                    this.getIntentNum()
                }
            },
            async getLogTableData (params) {
                this.taskExecutionLogTable.loading = true
                const response = await this.$store.dispatch('chart/getLogTableData', params, {})
                this.taskExecutionLogTable.data = response.data || []
                this.taskExecutionLogTable.loading = false
            },
            async getRecordTableData (params) {
                this.taskRecordTable.loading = true
                const response = await this.$store.dispatch('chart/getRecordTableData', params, {})
                this.taskRecordTable.data = response.data || []
                this.taskRecordTable.loading = false
            },
            async getBotNum () {
                const response = await this.$store.dispatch('chart/getBotNum', { 'bizId': this.bizId }, {})
                const data = response.data || {}
                this.botNum = data['count']
            },
            async getIntentNum () {
                const response = await this.$store.dispatch('chart/getIntentNum', { 'bizId': this.bizId }, {})
                const data = response.data || {}
                this.intentNum = data['count']
            }
        }
    }
</script>

<style>
    @import './index.css';
</style>
