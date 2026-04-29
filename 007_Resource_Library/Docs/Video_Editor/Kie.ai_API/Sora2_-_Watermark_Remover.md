---
title: "Sora2 - Watermark Remover"
type: spec
domain: video-production
tags: [spec, video-production, kie-ai, video-generation]
---

# Sora2 - Watermark Remover

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/jobs/createTask:
    post:
      summary: Sora2 - Watermark Remover
      deprecated: false
      description: >-
        Content generation using sora-watermark-remover


        ## Query Task Status


        After submitting a task, use the unified query endpoint to check
        progress and retrieve results:


        <Card title="Get Task Details" icon="lucide-search"
        href="/market/common/get-task-detail">
           Learn how to query task status and retrieve generation results
        </Card>


        ::: tip[]

        For production use, we recommend using the `callBackUrl` parameter to
        receive automatic notifications when generation completes, rather than
        polling the status endpoint.

        :::


        ## Related Resources


        <CardGroup cols={2}>
          <Card title="Market Overview" icon="lucide-store" href="/market/quickstart">
            Explore all available models
          </Card>
          <Card title="Common API" icon="lucide-cog" href="/common-api/get-account-credits">
            Check credits and account usage
          </Card>
        </CardGroup>
      operationId: sora-watermark-remover
      tags:
        - docs/en/Market/Video Models/Sora2
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - model
              properties:
                model:
                  type: string
                  enum:
                    - sora-watermark-remover
                  default: sora-watermark-remover
                  description: |-
                    The model name to use for generation. Required field.

                    - Must be `sora-watermark-remover` for this endpoint
                  examples:
                    - sora-watermark-remover
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive generation task completion updates.
                    Optional but recommended for production use.


                    - System will POST task status and results to this URL when
                    generation completes

                    - Callback includes generated content URLs and task
                    information

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing results

                    - Alternatively, use the Get Task Details endpoint to poll
                    task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://your-domain.com/api/callback
                input:
                  type: object
                  description: Input parameters for the generation task
                  properties:
                    video_url:
                      description: >-
                        Enter the Sora 2 video URL — it must be a publicly
                        accessible link from OpenAI (starting with
                        sora.chatgpt.com). (Max length: 500 characters)
                      type: string
                      maxLength: 500
                      examples:
                        - >-
                          https://sora.chatgpt.com/p/s_68e83bd7eee88191be79d2ba7158516f
                  required:
                    - video_url
                  x-apidog-orders:
                    - video_url
                    - 01KH0FGH7Y80Q0FG475XE754KH
                  x-apidog-refs:
                    01KH0FGH7Y80Q0FG475XE754KH:
                      type: object
                      properties: {}
                  x-apidog-ignore-properties: []
              x-apidog-orders:
                - model
                - callBackUrl
                - input
              x-apidog-ignore-properties: []
            example:
              model: sora-watermark-remover
              callBackUrl: https://your-domain.com/api/callback
              input:
                video_url: https://sora.chatgpt.com/p/s_68e83bd7eee88191be79d2ba7158516f
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
              example:
                code: 200
                msg: success
                data:
                  taskId: task_sora-watermark-remover_1765183831860
          headers: {}
          x-apidog-name: ''
      security:
        - BearerAuth: []
          x-apidog:
            schemeGroups:
              - id: kn8M4YUlc5i0A0179ezwx
                schemeIds:
                  - BearerAuth
            required: true
            use:
              id: kn8M4YUlc5i0A0179ezwx
            scopes:
              kn8M4YUlc5i0A0179ezwx:
                BearerAuth: []
      x-apidog-folder: docs/en/Market/Video Models/Sora2
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506414-run
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          enum:
            - 200
            - 401
            - 402
            - 404
            - 422
            - 429
            - 455
            - 500
            - 501
            - 505
          description: |-
            响应状态码

            - **200**: 成功 - 请求已处理完成
            - **401**: 未授权 - 身份验证凭据缺失或无效
            - **402**: 积分不足 - 账户积分不足以执行该操作
            - **404**: 未找到 - 请求的资源或端点不存在
            - **422**: 验证错误 - 请求参数未通过校验
            - **429**: 速率限制 - 已超出该资源的请求频次限制
            - **455**: 服务不可用 - 系统正在维护中
            - **500**: 服务器错误 - 处理请求时发生意外故障
            - **501**: 生成失败 - 内容生成任务执行失败
            - **505**: 功能禁用 - 当前请求的功能暂未开放
        msg:
          type: string
          description: 响应消息，请求失败时为错误描述
          examples:
            - success
      x-apidog-orders:
        - code
        - msg
      x-apidog-ignore-properties: []
      x-apidog-folder: ''
  securitySchemes:
    BearerAuth:
      type: bearer
      scheme: bearer
      bearerFormat: API Key
      description: |-
        所有 API 都需要通过 Bearer Token 进行身份验证。

        获取 API Key：
        1. 访问 [API Key 管理页面](https://kie.ai/api-key) 获取您的 API Key

        使用方法：
        在请求头中添加：
        Authorization: Bearer YOUR_API_KEY

        注意事项：
        - 请妥善保管您的 API Key，切勿泄露给他人
        - 若怀疑 API Key 泄露，请立即在管理页面重置
servers:
  - url: https://api.kie.ai
    description: 正式环境
security:
  - BearerAuth: []
    x-apidog:
      schemeGroups:
        - id: kn8M4YUlc5i0A0179ezwx
          schemeIds:
            - BearerAuth
      required: true
      use:
        id: kn8M4YUlc5i0A0179ezwx
      scopes:
        kn8M4YUlc5i0A0179ezwx:
          BearerAuth: []


import http.client
import json

conn = http.client.HTTPSConnection("api.kie.ai")
payload = json.dumps({
   "model": "sora-watermark-remover",
   "callBackUrl": "https://your-domain.com/api/callback",
   "input": {
      "video_url": "https://sora.chatgpt.com/p/s_68e83bd7eee88191be79d2ba7158516f"
   }
})
headers = {
   'Authorization': 'Bearer <token>',
   'Content-Type': 'application/json'
}
conn.request("POST", "/api/v1/jobs/createTask", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

import requests
import json

url = "https://api.kie.ai/api/v1/jobs/createTask"

payload = json.dumps({
   "model": "sora-watermark-remover",
   "callBackUrl": "https://your-domain.com/api/callback",
   "input": {
      "video_url": "https://sora.chatgpt.com/p/s_68e83bd7eee88191be79d2ba7158516f"
   }
})
headers = {
   'Authorization': 'Bearer <token>',
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```