'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Button, Switch, Select, message } from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'

interface MultimodalConfig {
  id: string
  tenant_id: string
  dataset_id: string
  image_model_provider?: string
  image_model_name?: string
  video_model_provider?: string
  video_model_name?: string
  enabled: boolean
  created_at?: string
  updated_at?: string
}

const MultimodalConfigPage = () => {
  const params = useParams()
  const datasetId = params.datasetId as string
  
  const [config, setConfig] = useState<MultimodalConfig | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  // 获取配置
  const fetchConfig = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/console/api/workspaces/current/datasets/${datasetId}/multimodal-config`)
      const data = await response.json()
      if (data.code === 0) {
        setConfig(data.data || {
          enabled: false,
          image_model_provider: 'openai',
          image_model_name: 'gpt-4-vision-preview',
          video_model_provider: 'openai',
          video_model_name: 'whisper-1'
        })
      }
    } catch (error) {
      message.error('获取配置失败')
    } finally {
      setLoading(false)
    }
  }

  // 保存配置
  const saveConfig = async (newConfig: Partial<MultimodalConfig>) => {
    setSaving(true)
    try {
      const response = await fetch(`/console/api/workspaces/current/datasets/${datasetId}/multimodal-config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newConfig),
      })
      const data = await response.json()
      if (data.code === 0) {
        message.success('配置保存成功')
        await fetchConfig()
      } else {
        message.error('配置保存失败')
      }
    } catch (error) {
      message.error('配置保存失败')
    } finally {
      setSaving(false)
    }
  }

  useEffect(() => {
    fetchConfig()
  }, [datasetId])

  const handleEnabledChange = (checked: boolean) => {
    if (config) {
      saveConfig({ ...config, enabled: checked })
    }
  }

  const handleModelChange = (type: 'image' | 'video', field: 'provider' | 'name', value: string) => {
    if (config) {
      const fieldName = `${type}_model_${field}` as keyof MultimodalConfig
      saveConfig({ ...config, [fieldName]: value })
    }
  }

  if (loading) {
    return <div>加载中...</div>
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">多模态配置</h2>
        <p className="text-gray-600">配置图片和视频的智能识别功能</p>
      </div>

      <div className="space-y-6">
        {/* 启用开关 */}
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div>
            <h3 className="font-medium">启用多模态处理</h3>
            <p className="text-sm text-gray-500">开启后，图片和视频文件将自动进行内容识别</p>
          </div>
          <Switch
            checked={config?.enabled || false}
            onChange={handleEnabledChange}
            loading={saving}
          />
        </div>

        {/* 图片模型配置 */}
        <div className="p-4 border rounded-lg">
          <h3 className="font-medium mb-4">图片识别模型</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">模型供应商</label>
              <Select
                value={config?.image_model_provider || 'openai'}
                onChange={(value) => handleModelChange('image', 'provider', value)}
                disabled={!config?.enabled}
                options={[
                  { label: 'OpenAI', value: 'openai' },
                  { label: '通义千问', value: 'tongyi' },
                ]}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">模型名称</label>
              <Select
                value={config?.image_model_name || 'gpt-4-vision-preview'}
                onChange={(value) => handleModelChange('image', 'name', value)}
                disabled={!config?.enabled}
                options={[
                  { label: 'GPT-4 Vision', value: 'gpt-4-vision-preview' },
                  { label: 'Qwen-VL-Plus', value: 'qwen-vl-plus' },
                ]}
              />
            </div>
          </div>
        </div>

        {/* 视频模型配置 */}
        <div className="p-4 border rounded-lg">
          <h3 className="font-medium mb-4">视频识别模型</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">模型供应商</label>
              <Select
                value={config?.video_model_provider || 'openai'}
                onChange={(value) => handleModelChange('video', 'provider', value)}
                disabled={!config?.enabled}
                options={[
                  { label: 'OpenAI', value: 'openai' },
                  { label: '通义千问', value: 'tongyi' },
                ]}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">模型名称</label>
              <Select
                value={config?.video_model_name || 'whisper-1'}
                onChange={(value) => handleModelChange('video', 'name', value)}
                disabled={!config?.enabled}
                options={[
                  { label: 'Whisper-1', value: 'whisper-1' },
                  { label: 'Qwen-Audio', value: 'qwen-audio' },
                ]}
              />
            </div>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex justify-end space-x-4">
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchConfig}
            loading={loading}
          >
            刷新
          </Button>
        </div>
      </div>
    </div>
  )
}

export default MultimodalConfigPage
