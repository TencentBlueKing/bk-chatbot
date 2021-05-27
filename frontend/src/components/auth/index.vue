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
    <div class="bk-login-dialog" v-if="isShow">
        <div class="bk-login-wrapper">
            <iframe :src="iframeSrc" scrolling="no" border="0" :width="iframeWidth" :height="iframeHeight"></iframe>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'app-auth',
        data () {
            return {
                iframeSrc: '',
                iframeWidth: 500,
                iframeHeight: 500,
                isShow: false
            }
        },
        methods: {
            hideLoginModal () {
                this.isShow = false
            },
            showLoginModal (data) {
                let url = data.login_url
                if (!url) {
                    const callbackUrl = `${location.origin}/static/login_success.html?is_ajax=1`
                    url = `/plain?c_url=${callbackUrl}`
                }
                this.iframeSrc = url
                const iframeWidth = data.width
                if (iframeWidth) {
                    this.iframeWidth = iframeWidth
                }
                const iframeHeight = data.height
                if (iframeHeight) {
                    this.iframeHeight = iframeHeight
                }
                setTimeout(() => {
                    this.isShow = true
                }, 1000)
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
