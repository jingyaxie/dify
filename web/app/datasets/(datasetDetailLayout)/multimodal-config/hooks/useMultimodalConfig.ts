import { useState, useEffect } from 'react'

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

export const useMultimodalConfig = (datasetId: string) => {
  const [config, setConfig] = useState<MultimodalConfig | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchConfig = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/console/api/workspaces/current/datasets/${datasetId}/multimodal-config`)
      const data = await response.json()
      if (data.code === 0) {
        setConfig(data.data || {
          enabled: true,
          image_model_provider: 'openai',
          image_model_name: 'gpt-4-vision-preview',
          video_model_provider: 'openai',
          video_model_name: 'whisper-1'
        })
      } else {
        setError(data.message || '获取配置失败')
      }
    } catch (err) {
      setError('网络错误')
    } finally {
      setLoading(false)
    }
  }

  const updateConfig = async (newConfig: Partial<MultimodalConfig>) => {
    setLoading(true)
    setError(null)
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
        setConfig(data.data)
        return { success: true }
      } else {
        setError(data.message || '更新配置失败')
        return { success: false, error: data.message }
      }
    } catch (err) {
      setError('网络错误')
      return { success: false, error: '网络错误' }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConfig()
  }, [datasetId])

  return {
    config,
    loading,
    error,
    fetchConfig,
    updateConfig,
  }
}
