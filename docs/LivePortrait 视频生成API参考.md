# LivePortrait 视频生成API参考

更新时间：2025-05-15 11:03:51

[产品详情](https://www.aliyun.com/product/bailian)

[我的收藏](https://help.aliyun.com/my_favorites.html)

LivePortrait模型，可基于通过LivePortrait-detect模型检测的人物肖像图片和人声音频文件，快速、轻量化地生成人像动态视频。本文档介绍了该模型提供的视频生成能力的API调用方法。

## 模型概览

|      |      |
| ---- | ---- |
|      |      |

| **模型名**   | **模型简介**                                                 |
| ------------ | ------------------------------------------------------------ |
| liveportrait | liveportrait是一个人物视频生成模型，可基于人物肖像图片和人声音频文件，快速、轻量化地生成人物肖像动态视频。 |

## HTTP调用接口

### 功能描述

用于生成人物肖像动态视频。

### 前提条件

- 已开通阿里云百炼服务并获得API-KEY：[获取API Key](https://help.aliyun.com/zh/model-studio/get-api-key)。
- 输入图像已通过[LivePortrait 图像检测API详情](https://help.aliyun.com/zh/model-studio/liveportrait-detect-api)检测。

### **输入限制**

- 图像格式：格式为jpeg、jpg、png、bmp、webp。
- 图像分辨率：图像文件<10M，宽高比≤2，最大边长≤4096像素。
- 音频格式：格式为wav、mp3。
- 音频限制：文件＜15M，1s＜时长＜5min。
- 音频内容：音频中需包含清晰、响亮的人声语音，并去除了环境噪音、背景音乐等声音干扰信息。
- 上传图片、音频链接仅支持HTTP链接方式，不支持本地链接方式。

### 作业提交接口

 

```http
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis/
```

**说明**

- 因该算法调用耗时较长，故采用异步调用的方式提交任务。
- 任务提交之后，系统会返回对应的作业ID，后续可通过“作业任务状态查询和结果获取接口”获取任务状态及对应结果。

#### **入参描述**

|      |      |      |      |      |      |
| ---- | ---- | ---- | ---- | ---- | ---- |
|      |      |      |      |      |      |

| **字段**                       | **类型** | **传参方式** | **必选** | **描述**                                                     | **示例值**                    |
| ------------------------------ | -------- | ------------ | -------- | ------------------------------------------------------------ | ----------------------------- |
| Content-Type                   | String   | Header       | 是       | 请求类型：application/json。                                 | application/json              |
| Authorization                  | String   | Header       | 是       | API-Key，例如：Bearer d1**2a。                               | Bearer d1**2a                 |
| X-DashScope-Async              | String   | Header       | 是       | 使用enable，表明使用异步方式提交作业。                       | enable                        |
| model                          | String   | Body         | 是       | 指明需要调用的模型，此处用liveportrait。                     | liveportrait                  |
| input.image_url                | String   | Body         | 是       | 用户上传的图片 URL，该图应先通过[LivePortrait图像检测API](https://help.aliyun.com/zh/model-studio/liveportrait-detect-api)。图像文件<10M，宽高比≤2，最大边长≤4096。格式支持：jpeg、jpg、png、bmp、webp。**说明**上传图片仅支持HTTP链接方式，不支持本地链接方式。 | "image_url": "http://a/a.jpg" |
| input.audio_url                | String   | Body         | 是       | 用户上传的音频文件 URL。音频文件＜15M，1s＜时长＜5min。格式支持：wav、mp3。**说明**上传文件仅支持HTTP链接方式，不支持本地链接方式。 | http://aaa/bbb.wav            |
| parameters.template_id         | String   | Body         | 否       | 可按模板控制人物头部的运动姿态和幅度，当前支持3种模板：normal、calm、active。默认为normal。 | "normal"                      |
| parameters.eye_move_freq       | Float    | Body         | 否       | 每秒眨眼次数，可设值为0-1，值越大眨眼频率越高。默认值为0.5。 | 0.5                           |
| parameters.video_fps           | Integer  | Body         | 否       | 输出视频帧率，可设值为15-30。默认值为24。                    | 24                            |
| parameters.mouth_move_strength | Float    | Body         | 否       | 嘴部动作的幅度大小，可设值为0-1.5，值越大嘴型越大。若设为0则嘴部无动作。默认值为1。 | 1                             |
| parameters.paste_back          | Boolean  | Body         | 否       | 生成的人脸是否贴回原图，可设值为true或false。若设为false则仅输出生成的人脸，忽略人物身体。默认值为true。 | true                          |
| parameters.head_move_strength  | Float    | Body         | 否       | 头部动作幅度，可设值为0-1，值越大头部动作幅度越大。默认值为0.7。 | 0.7                           |

#### **出参描述**

|      |      |      |      |
| ---- | ---- | ---- | ---- |
|      |      |      |      |

| **字段**           | **类型** | **描述**                                                     | **示例值**                           |
| ------------------ | -------- | ------------------------------------------------------------ | ------------------------------------ |
| output.task_id     | String   | 提交异步任务的作业id，实际作业结果需要通过异步任务查询接口获取。 | a8532587-fa8c-4ef8-82be-0c46b17950d1 |
| output.task_status | String   | 提交异步任务后的作业状态。                                   | “PENDING”                            |
| request_id         | String   | 本次请求的系统唯一码。                                       | 7574ee8f-38a3-4b1e-9280-11c33ab46e51 |

#### **可选用的动作模板**

|      |      |
| ---- | ---- |
|      |      |

| **template_id** | **效果说明**                                         |
| --------------- | ---------------------------------------------------- |
| normal          | 默认动作模板，头部动作幅度适中。适用于多种场景。     |
| calm            | 人物表现平静，头部动作幅度较小。推荐用于播报等场景。 |
| active          | 人物表现活泼，头部动作幅度较大。推荐用于演唱等场景。 |

#### **请求示例**

 

```curl
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis/' \
--header 'X-DashScope-Async: enable' \
--header 'Authorization: Bearer <YOUR_API_KEY>' \
--header 'Content-Type: application/json' \
--data '{
    "model": "liveportrait",
    "input": {
        "image_url": "http://xxx/1.jpg",
        "audio_url": "http://xxx/1.wav"
    },
      "parameters": {
         "template_id": "normal",
         "eye_move_freq": 0.5,
         "video_fps":30,
         "mouth_move_strength":1,
         "paste_back": true,
         "head_move_strength":0.7
    }
  }'
```

#### **响应示例**

 

```json
{
    "output": {
	"task_id": "a8532587-fa8c-4ef8-82be-0c46b17950d1", 
    	"task_status": "PENDING"
    }
    "request_id": "7574ee8f-38a3-4b1e-9280-11c33ab46e51"
}
```

### **作业任务状态查询和结果获取接口**

 

```http
GET https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}
```

#### **入参描述**

|      |      |      |      |      |      |
| ---- | ---- | ---- | ---- | ---- | ---- |
|      |      |      |      |      |      |

| **字段**      | **类型** | **传参方式** | **必选** | **描述**                       | **示例值**                           |
| ------------- | -------- | ------------ | -------- | ------------------------------ | ------------------------------------ |
| Authorization | String   | Header       | 是       | API-Key，例如：Bearer d1**2a。 | Bearer d1**2a                        |
| task_id       | String   | Url Path     | 是       | 需要查询作业的 task_id。       | a8532587-fa8c-4ef8-82be-0c46b17950d1 |

#### **出参描述**

|      |      |      |      |
| ---- | ---- | ---- | ---- |
|      |      |      |      |

| **字段**                 | **类型** | **描述**                                                     | **示例值**                                                   |
| ------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| output.task_id           | String   | 查询作业的 task_id。                                         | a8532587-fa8c-4ef8-82be-0c46b17950d1                         |
| output.task_status       | String   | 被查询作业的作业状态。                                       | 任务状态：PENDING 排队中RUNNING 处理中SUCCEEDED 成功FAILED 失败UNKNOWN 作业不存在或状态未知 |
| output.results.video_url | String   | 如果作业成功，包含模型生成的结果 object，然后每个 object 中包含按照要求生成的结果地址。**video_url有效期为作业完成后24小时**。 | https://xxx/1.mp4                                            |
| usage.video_duration     | Float    | 本次请求生成视频时长计量，单位：秒。                         | 10.23                                                        |
| usage.video_ratio        | String   | 本次请求生成视频的画幅类型，该值为standard。                 | "video_ratio": "standard"                                    |
| request_id               | String   | 本次请求的系统唯一码。                                       | 7574ee8f-38a3-4b1e-9280-11c33ab46e51                         |

#### **请求示例**

 

```curl
curl -X GET \
--header 'Authorization: Bearer <YOUR_API_KEY>' \
https://dashscope.aliyuncs.com/api/v1/tasks/<YOUR_TASK_ID>
```

#### **响应示例（**作业成功执行完毕**）**

 

```json
{
    "request_id":"7574ee8f-38a3-4b1e-9280-11c33ab46e51",
    "output":{
        "task_id":"a8532587-fa8c-4ef8-82be-0c46b17950d1",
	"task_status":"SUCCEEDED",
        "results":{
            "video_url":"https://xxx/1.mp4"
        }
    },
    "usage":{
        "video_duration": 10.23,
        "video_ratio": "standard"
    }
}
```

#### 响应示例（作业失败）

 

```json
{
    "request_id": "7574ee8f-38a3-4b1e-9280-11c33ab46e51"
    "output": {
        "task_id": "a8532587-fa8c-4ef8-82be-0c46b17950d1", 
    	"task_status": "FAILED",
    	"code": "xxx", 
    	"message": "xxxxxx", 
    }  
}
```

## 状态码说明

大模型服务平台通用状态码请查阅：[错误信息](https://help.aliyun.com/zh/model-studio/error-code)。

本模型还有如下特定错误码：

| **http 返回码\*** | **错误码（code）** | **错误信息（message）** | **含义说明** |
| ----------------- | ------------------ | ----------------------- | ------------ |
|                   |                    |                         |              |

| **http 返回码\*** | **错误码（code）**                     | **错误信息（message）**                                   | **含义说明**                                                 |
| ----------------- | -------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------ |
| 400               | InvalidParameter.UnsupportedFileFormat | Input files format not supported.                         | 音频、图片格式不符合要求。音频支持格式mp3, wav, aac;图片支持格式jpg, jpeg, png, bmp, webp。 |
| 400               | InvalidParameter.InputDownloadFailed   | Failed to download input files.                           | 输入文件下载失败                                             |
| 400               | InvalidImage.ImageSize                 | The size of image is beyond limit.                        | 图片大小超出限制。要求图片长宽比例不大于2，且最长边不大于4096。 |
| 400               | InvalidFile.AudioLengthError           | Audio length must be between 1s and 300s.                 | 音频长度不符合要求（应在[1, 300]秒范围内）                   |
| 400               | InvalidImage.NoHumanFace               | No human face detected.                                   | 未检测到人脸（仅生成任务异步查询接口）                       |
| 400               | InvalidParamter.OutOfDefinition        | The type or value of {parameter} is out of definition.    | 参数类型或值不符合要求                                       |
| 500               | InternalError.Algo                     | An internal error has occured during algorithm execution. | 算法运行时发生错误                                           |
| 500               | InternalError.Upload                   | Failed to upload result.                                  | 生成结果上传失败                                             |