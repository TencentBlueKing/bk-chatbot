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
    <div class="exception-box">
        <img src="@/images/404.png" alt="">
        <p>没找到页面！</p>
    </div>
</template>

<script>
    export default {
        data () {
            return {}
        }
    }
</script>

<style scoped lang="postcss">
    .exception-box {
        text-align: center;
        margin: auto;
        img {
            width: 300px;
            margin-top: 150px;
        }
        p {
            font-size: 20px;
            color: #979797;
            margin: 32px 0;
            font-weight: 400;
        }
    }
</style>
